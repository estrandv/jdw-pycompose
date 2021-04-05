from __future__ import annotations
from typing import Iterable
from composer import PostingType, PostingTypes
from scales import CHROMATIC, transpose
from parsing import parse_note
from copy import deepcopy
from pretty_midi.utilities import note_number_to_hz

# Transform any set of integer lists into the sheet-standard of "0 0 0 . 1 0 1" etc. 
# Each list is another chunk separated by a dot, the above would be the same as: [0,0,0], [1,0,1]
# Useful if you want to utilize python list generators such as range()
def arr_fmt(*lists: Iterable[int]) -> str:
    ret_str = ""
    string_lists = [[str(i) for i in lst] for lst in lists]
    return " . ".join([" ".join(slst) for slst in string_lists])

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

class MetaSheet:

    # Args outline data needed to post to the jdw-sequencer and, ultimately, to PROSC or MIDI 
    def __init__(self, instrument: str, sequencer_id: str, posting: PostingType):
        self.posing_type: PostingType = posting
        self.instrument: str = instrument
        self.sequencer_id: str = sequencer_id
        self.sheets: list[Sheet] = []

    # Create and save a new sheet 
    def sheet(self, source: str, scale: list[int] = CHROMATIC, octave: int = 4) -> Sheet:
        sheet = Sheet(self, source)
        self.sheets.append(sheet)
        return sheet
   
    # Add a silent sheet of <time> length 
    def pad(self, time: float) -> MetaSheet:
        self.sheet("0", CHROMATIC, 0).all("amp0 res" + str(time))
        return self

    # Returns total length of all sheets 
    def len(self) -> float:
        return sum([sheet.len() for sheet in self.sheets])

class Sheet:
    # Accepts the syntax "0 1 3 0 . 0 1 1 1" where dots are used to separate sections of tones
    def __init__(self, meta_sheet: MetaSheet, source: str, scale: list[int] = CHROMATIC, octave: int = 4):
        
        self.meta_sheet = meta_sheet
        self.scale = scale
        self.octave = octave

        self.part_indices: list[int] = [0]
        all_tones: list[float] = []

        for chunk in source.split(" "):
            if chunk.isdigit():
                all_tones.append(float(chunk))
            elif chunk == ".":
                self.part_indices.append(len(all_tones))
            else:
                print("ERROR: Bad symbol(s): " + chunk)
                break

        self.notes: list[dict[str, float]] = []
        for tone in all_tones:
            self.notes.append({"tone": tone})


    # on_note, all and part_step all overwrite the notes at the given positions 
    # with the provided attributes, e.g. "res20 amp35"
    # human-read based, ie starts on "1" as first note 
    def on_note(self, note_nums: list[int], attributes: str) -> Sheet:

        override = _parse_note(attributes)

        for i in note_nums:
            if i < 1:
                print("Error: note count starts at 1")
                break
            self.notes[i - 1] = _merge_note(self.notes[i - 1], override)

        return self

    def all(self, attributes: str) -> Sheet:
        override = _parse_note(attributes)

        for i in range(len(self.notes)):
            self.notes[i] = _merge_note(self.notes[i], override)

        return self
    
    # Similar to above but based on the dot-defined "parts" in the sheet 
    def part_step(self, note_nums: list[int], attributes: str) -> Sheet:
        override = _parse_note(attributes)

        for p in self.part_indices:
            for i in note_nums:
                if i < 1:
                    print("Error: note count starts at 1")
                self.notes[p + i - 1] = _merge_note(self.notes[p + i - 1], override)

        return self

    def len(self) -> float:
        return sum([note["reserved_time"] for note in self.notes])
   
    # Apply scale and octave to all contained notes and change midi-tones to actual corresponding note hz 
    def to_notes(self, to_hz = True) -> list[dict[str, float]]:
        
        def midi_format(note: dict[str, float]):

            midi_tone = note["tone"]
            extra = 0
            if self.octave > 0:
                extra = (12 * (self.octave - 1))

            ocatave_tone = extra + midi_tone
            transposed_tone = transpose(int(ocatave_tone), self.scale)

            if to_hz:
                note["tone"] = transposed_tone
            else:
                note["tone"] = note_number_to_hz(transposed_tone)

        exported = []

        for note in self.notes:
            new = deepcopy(note)
            midi_format(new)
            exported.append(new)

        return exported

# Testing
meta_sheet = MetaSheet("", "", PostingTypes.PROSC)
sheet = meta_sheet.sheet("0 13 4 3 . 8 6 2 1 . 0 4 22 4")

sheet.on_note([1, 5, 9], "=20")
sheet.part_step([1], ">40")

def attr_assert(index: int, attr: str, target: float):
    assert sheet.notes[index][attr] == target, "Wrong " + attr + ": " + str(sheet.notes[index][attr])

attr_assert(0, "tone", 0.0)
attr_assert(1, "tone", 13.0)
attr_assert(10, "tone", 22.0)

attr_assert(0, "reserved_time", 2.0)
attr_assert(4, "reserved_time", 2.0)

attr_assert(8, "sus", 4.0)
attr_assert(0, "sus", 4.0)

len_sheet = meta_sheet.sheet("0 0 0 0").all("=15")

assert len_sheet.len() == 6.0, "Unexpected total res: " + str(len_sheet.len())

assert arr_fmt([0,1,22], [0,2,0], [0,0,1,0]) == "0 1 22 . 0 2 0 . 0 0 1 0", "Bad arr_fmt: " + arr_fmt([0,1,22], [0,2,0], [0,0,1,0]) 
print(arr_fmt(range(0, 14), range(0,3)))
