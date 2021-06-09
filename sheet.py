from __future__ import annotations
import json
from typing import Any, Iterable
from scales import CHROMATIC, transpose
from parsing import parse_note
from copy import deepcopy
from pretty_midi.utilities import note_number_to_hz
import zmq_client 



class PostingType:
    def __init__(self, id: int):
        self.id = id

class PostingTypes:
    PROSC = PostingType(0)
    SAMPLE = PostingType(1)
    MIDI = PostingType(2)

# Transform the local note dict into the api expected format 
# TODO: Bit of a mess, but the end goal is to transform notes into the zeromq sequencer format
def _export_note(note: dict[str, float], synth_name: str, sequencer_id: str, posting_type: PostingType):
    # {alias, time, "msg: XXX::{target, args}"}
    sequencer_message: dict[str, Any] = {"alias": sequencer_id}
    exported = {"target": synth_name, "args": {}}

    amp = 0.0

    for key in note:

        # TODO: Dirty hack until harmonized
        if key == "tone":
            exported["args"]["freq"] = note[key]
        elif key == "reserved_time": # TODO: Also clumsy 
            sequencer_message["time"] = note[key]            
        else:
            exported["args"][key] = note[key]
            if key == "amp":
                amp = note[key]

    payload = json.dumps(exported)

    # Don't order sequencer to actually play any "silent" notes
    if amp == 0.0:
        payload = "{}"

    if posting_type == PostingTypes.PROSC:
        sequencer_message["msg"] = "JDW.PLAY.NOTE::" + payload
    elif posting_type == PostingTypes.SAMPLE:
        sequencer_message["msg"] = "JDW.PLAY.SAMPLE::" + payload
    elif posting_type == PostingTypes.MIDI:
        # TODO: Malformed, needs a lot more processing, including real time sus
        sequencer_message["msg"] = "JDW.PLAY.MIDI::" + payload

    return sequencer_message


# Transform any set of integer lists into the sheet-standard of "0 0 0 . 1 0 1" etc. 
# Each list is another chunk separated by a dot, the above would be the same as: [0,0,0], [1,0,1]
# Useful if you want to utilize python list generators such as range()
def arr_fmt(*lists: Iterable[int]) -> str:
    return " . ".join([" ".join(slst) for slst in [[str(i) for i in lst] for lst in lists]])

def _merge_note(under: dict[str, float], over: dict[str, float]) -> dict[str, float]:
    
    merged = deepcopy(under)

    for attr in over:
        merged[attr] = over[attr]

    return merged

# Note: This is a hack. For convenience, the original parse_note expects tone as first arg
# but we don't in this scenario. Will probably support this natively soon...
def _parse_note(string: str) -> dict[str, float]:
    note = parse_note("0 " + string)
    note.pop("tone", None)
    return note

# Helper class for managing multiple MetaSheets. Plays the role of a "timeline" in composition as 
# well as main UI for quickly changing large parts of the composition (e.g. mute everything)
# All metaSheets added via reg() are affected by composer calls. 
class Composer:
    def __init__(self) -> None:
        self.meta_sheets: list[MetaSheet] = []
        self.client = zmq_client.PublisherClient()
        self.last_sync_time = 0.0
        self.restart_sheet_indices: dict[str, int] = {}


    def reg(self, meta_sheet: MetaSheet) -> MetaSheet:
        self.meta_sheets.append(meta_sheet)
        return meta_sheet
    
    # Pad all sheets with silence until everything is the same length 
    def sync(self) -> Composer:
        for meta_sheet in self.meta_sheets:
            diff = self.len() - meta_sheet.len()
            if diff > 0.0:
                meta_sheet.pad(diff)

        self.last_sync_time = self.len()
        return self 

    def cont(self, mss: list[MetaSheet]) -> Composer:
        for ms in mss:
            ms.cont()

        return self

    # Convenience call to be placed in the middle of active compositions 
    # See usage of restart indices in post_all; effectively says not to play anything up until this point
    def restart(self) -> Composer:
        for ms in self.meta_sheets:
            if len(ms.sheets) > 0:
                self.restart_sheet_indices[ms.sequencer_id] = len(ms.sheets)

        return self

    # Detects which sheets were played since last sync() call and repeats 
    # those to match the longest one (i.e. "play and repeat together")
    def smart_sync(self, exclude: list[MetaSheet]=[]) -> Composer:
        
        played_since_sync = [meta_sheet for meta_sheet in self.meta_sheets if meta_sheet.len() > self.last_sync_time]
        longest_recent = [ms for ms in self.meta_sheets if ms.len() == self.len()][0]

        ex_alias = [ms.sequencer_id for ms in exclude]

        for ms in played_since_sync:
            if ms.sequencer_id not in ex_alias:
                ms.reach(self.len()) 
            else: 
                print("excluding " + ms.sequencer_id)

        self.sync()

        print("AFTER SYNC: " + str(self.len()))
        for note_set in [ms.sequencer_id + str(ms.sheets[-1].notes) for ms in self.meta_sheets if len(ms.sheets) > 0]:
            print("   - " + note_set)

        return self 

    # Return the end point of the composer timeline; the length of the longest contained metasheet 
    def len(self) -> float:
        return max([ms.len() for ms in self.meta_sheets])

    # Post export and post everything to jdw-sequencer 
    def post_all(self):
        for meta_sheet in self.meta_sheets:

            if meta_sheet.sequencer_id in self.restart_sheet_indices:
                meta_sheet.sheets = meta_sheet.sheets[self.restart_sheet_indices[meta_sheet.sequencer_id]:]

            self.client.queue(meta_sheet.export_all())


class MetaSheet:

    # Args outline data needed to post to the jdw-sequencer and, ultimately, to PROSC or MIDI 
    # Note the pass-along "to_hz", which should typically be set to false for SAMPLE posting 
    def __init__(self, sequencer_id: str, instrument: str, posting: PostingType, to_hz = True):
        self.posting_type: PostingType = posting
        self.instrument: str = instrument
        self.sequencer_id: str = sequencer_id
        self.sheets: list[Sheet] = []
        self.to_hz = to_hz
        self.clipboard: dict[str, Sheet] = {}
        
    # Create and save a new sheet 
    def sheet(self, source: str, scale: list[int] = CHROMATIC, octave: int = 0) -> Sheet:
        sheet = Sheet(self, source, scale, octave)
        self.sheets.append(sheet)
        # TODO: Check that we don't add defaults anywhere else 
        sheet.all("=10 >10 #10")
        return sheet

    # Grab a previously copy():d sheet by name and add it to the end of sheet (returning it)
    # Note deepcopy() - it's a copy of the copy, not the original sheet instance 
    def paste(self, clipboard_name: str) -> Sheet:
        if clipboard_name in self.clipboard:
            sheet = deepcopy(self.clipboard[clipboard_name])
            self.sheets.append(sheet)
            return sheet

        print("ERROR: Copied sheet with name", clipboard_name, "not found")
        return Sheet(self, "")

    # Play the latest sheet again if exists 
    def cont(self, times=1) -> MetaSheet:
        if len(self.sheets) > 0:
            for i in range(0, times):
                self.sheets.append(deepcopy(self.sheets[-1]))

        return self

    # Repeat latest registered sheet until total length matches <length>, padding any remains
    def reach(self, length: float) -> MetaSheet:
        diff = length - self.len()
        if len(self.sheets) > 0:
            latest = deepcopy(self.sheets[-1])
            if latest.len() <= diff:
                self.sheets.append(latest)
            elif diff > 0.0:
                self.pad(diff)

            if self.len() < length:
                return self.reach(length)

        elif diff > 0.0:
            self.pad(diff)

        return self 
   
    # Add a silent sheet of <time> length 
    def pad(self, time: float) -> MetaSheet:
        # Bit hacky to use the native string parse method (note the *10) but it works for now...
        self.sheet("0", CHROMATIC, 0).all("#0 =" + str(time * 10))
        return self

    # Returns total length of all sheets 
    def len(self) -> float:
        return sum([sheet.len() for sheet in self.sheets])

    # Get all notes from all sheets in order and make them sequencer-compatible
    def export_all(self) -> list[dict]:
        all_notes: list[dict[str,float]] = [note for sublist in [sheet.to_notes(self.to_hz) for sheet in self.sheets] for note in sublist]
        return [_export_note(note, self.instrument, self.sequencer_id, self.posting_type) for note in all_notes]
        

class Sheet:
    # Accepts the syntax "0 1 3 0 . 0 1 1 1" where dots are used to separate sections of tones
    def __init__(self, meta_sheet: MetaSheet, source: str, scale: list[int] = CHROMATIC, octave: int = 4):
        
        self.meta_sheet = meta_sheet
        self.scale = scale
        self.octave = octave

        self.part_indices: list[int] = [0]
        
        # Typing e.g. "18a 12boo" will tag the first note as "a" and the second as "boo"
        # See the tagged() call 
        self.tagged_indices: dict[str, list[int]] = {}

        all_tones: list[float] = []

        for chunk in source.split(" "):
            if any(char.isdigit() for char in chunk):

                first = chunk[0]

                if first.isdigit():
                    
                    # Scan until whole unbroken digit found 
                    digit_part = ""
                    for char in chunk:
                        if char.isdigit():
                            digit_part += char
                        else:
                            break

                    # Add the tone 
                    all_tones.append(float(digit_part))

                    # The following part becomes the tag 
                    tag = chunk.replace(digit_part, "")
                    if tag not in self.tagged_indices:
                        self.tagged_indices[tag] = []
                    self.tagged_indices[tag].append(len(all_tones) - 1) # Index of the tone we just added

                else:
                    print("ERROR: note chunk", chunk, "must have digit as first char!")

            elif chunk == ".":
                self.part_indices.append(len(all_tones))
            else:
                print("ERROR: Bad symbol(s): " + chunk)
                break

        self.notes: list[dict[str, float]] = []
        for tone in all_tones:
            self.notes.append({"tone": tone})

    def all(self, attributes: str) -> Sheet:
        override = _parse_note(attributes)

        for i in range(len(self.notes)):
            self.notes[i] = _merge_note(self.notes[i], override)

        return self

    def tagged(self, tag: str, attributes: str) -> Sheet:
        override = _parse_note(attributes)
        
        if tag in self.tagged_indices:
            for index in self.tagged_indices[tag]:
                self.notes[index] = _merge_note(self.notes[index], override)
        else:
            print("WARN: Tag missing:", tag)

        return self 

    
    # Modify dots by their ordinal since last dot, e.g. [2] = "0 1 0 0 . 0 1 0 0"
    def dots(self, note_nums: list[int], attributes: str) -> Sheet:
        override = _parse_note(attributes)

        for p in self.part_indices:
            for i in note_nums:
                if i < 1:
                    print("Error: note count starts at 1")
                self.notes[p + i - 1] = _merge_note(self.notes[p + i - 1], override)

        return self

    # See MetaSheet.paste() 
    def copy(self, name: str) -> Sheet:
        self.meta_sheet.clipboard[name] = deepcopy(self)
        return self

    # Like copy, but removing itself from the meta_sheet
    def cut(self, name: str) -> Sheet:
        self.copy(name)
        self.meta_sheet.sheets.remove(self)
        return self

    # Double own notes <times> amount of times
    # TODO: Does not account for part sections or tags, dangerous!
    def stretch(self, times: int) -> Sheet:
        appenders = deepcopy(self.notes)

        for i in range(0, times):
            self.notes += appenders
        return self

    def len(self) -> float:
        return sum([note["reserved_time"] for note in self.notes]) if len(self.notes) > 0 else 0.0
   
    # Apply scale and octave to all contained notes and change midi-tones to actual corresponding note hz 
    def to_notes(self, to_hz = True) -> list[dict[str, float]]:
        
        def midi_format(input_note: dict[str, float]):

            note = deepcopy(input_note)

            midi_tone = note["tone"]
            extra = 0
            if self.octave > 0:
                extra = (12 * (self.octave - 1))

            ocatave_tone = extra + midi_tone
            transposed_tone = transpose(int(ocatave_tone), self.scale)

            if not to_hz:
                note["tone"] = transposed_tone
            else:
                note["tone"] = note_number_to_hz(transposed_tone)

            return note 

        exported = []

        for note in self.notes:
            formatted = midi_format(note)
            
            # Force existance of "required" attributes
            # This might be subject to change later 
            def require(attr: str):
                if attr not in formatted:
                    formatted[attr] = 1.0 

            require("amp")
            require("sus")
            require("reserved_time")
            

            exported.append(formatted)

        return exported

# Testing
meta_sheet = MetaSheet("", "", PostingTypes.PROSC)
sheet = meta_sheet.sheet("0 13 4 3 . 8 6 2 1 . 0 4 22 4")

sheet.dots([1], ">40")

def attr_assert(index: int, attr: str, target: float):
    assert sheet.notes[index][attr] == target, "Wrong " + attr + ": " + str(sheet.notes[index][attr])

attr_assert(0, "tone", 0.0)
attr_assert(1, "tone", 13.0)
attr_assert(10, "tone", 22.0)

attr_assert(8, "sus", 4.0)
attr_assert(0, "sus", 4.0)

len_sheet = meta_sheet.sheet("0 0 0 0").all("=15")

assert len_sheet.len() == 6.0, "Unexpected total res: " + str(len_sheet.len())

assert arr_fmt([0,1,22], [0,2,0], [0,0,1,0]) == "0 1 22 . 0 2 0 . 0 0 1 0", "Bad arr_fmt: " + arr_fmt([0,1,22], [0,2,0], [0,0,1,0]) 

mscont = MetaSheet("", "", PostingTypes.PROSC)
cont_s = mscont.sheet("2 3 4 5").all("=10").dots([1], "=50")
mscont.cont()
assert len(mscont.sheets) == 2
assert mscont.sheets[-1].notes[0]["reserved_time"] == 5.0
assert mscont.sheets[-2].notes[0]["reserved_time"] == 5.0


