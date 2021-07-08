from __future__ import annotations
from typing import Any, Iterable
from parsing import compile_sheet, parse_args
from scales import CHROMATIC, transpose
from pretty_midi.utilities import note_number_to_hz
from notifypy import Notify # Desktop notifications for debug
import zmq_client 
from sheet_utils import PostingType, PostingTypes, _merge_note, _export_note, arr_fmt
from copy import deepcopy

def copy_sheet(sheet: 'Sheet') -> 'Sheet':
    copy = Sheet(sheet.meta_sheet, sheet.source, sheet.scale, sheet.octave)
    copy.notes = deepcopy(sheet.notes)
    copy.part_indices = sheet.part_indices
    copy.tagged_indices = sheet.tagged_indices
    copy.debug_mark = sheet.debug_mark

    return copy

class Sheet:
    # Accepts the syntax "0 1 3 0 . 0 1 1 1" where dots are used to separate sections of tones
    def __init__(self, meta_sheet: 'MetaSheet', source: str, scale: list[int] = CHROMATIC, octave: int = 4):

        # save the source in case you need it for making copies
        self.source = source

        self.meta_sheet = meta_sheet
        self.scale = scale
        self.octave = octave

        self.part_indices: list[int] = [0]
        
        # Typing e.g. "18a 12boo" will tag the first note as "a" and the second as "boo"
        # See the tagged() call 
        self.tagged_indices: dict[str, list[int]] = {}

        # When debug is called on the composer level, this is used to display a debug message if non-blank
        self.debug_mark = ""

        self.notes: list[dict[str, float]] = []

        # Count non-bracketed spaces as "note splits"
        # Basically: "0 0[=.5 >.4]" -> "0<DIVIDE>0[=.5 >.4]"
        # Prone to silliness if you don't close your brackets.
        # Just close your damn brackets. 
        space_scan = ""
        bracket_open = False
        for letter in compile_sheet(source):
            if letter == " " and not bracket_open:
                space_scan += "<DIVIDE>"
            else:
                if letter == "[" and not bracket_open:
                    bracket_open = True
                elif letter == "]":
                    bracket_open = False
                space_scan += letter

        for chunk in space_scan.split("<DIVIDE>"):
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
                    self.notes.append({"tone": float(digit_part), "amp": 1.0, "sus": 1.0, "reserved_time": 1.0})

                    # Process the part after the digits (inline or tag)
                    after_digits = chunk.replace(digit_part, "")
                    tag = after_digits
                    if after_digits != "":
                        # Brackets are effectiely an inline tag
                        if after_digits[0] == "[":
                            if "]" in after_digits:
                                # [...] -> ...
                                contained = "".join("".join(after_digits.split("[")[1:]).split("]")[:-1])
                                
                                # Turn contained args into dict
                                override = eargs(contained)

                                # Note defaults are applied here
                                self.notes[-1] = _merge_note(self.notes[-1], override)
                                tag = after_digits.replace("[" + contained + "]", "")

                            else:
                                print("Error: Unclosed brackets tag")
                    
                    if tag not in self.tagged_indices:
                        self.tagged_indices[tag] = []
                    self.tagged_indices[tag].append(len(self.notes) - 1) # Index of the tone we just added

                else:
                    print("ERROR: note chunk", chunk, "must have digit as first char!")

            elif chunk == ".":
                self.part_indices.append(len(self.notes))
            else:
                print("ERROR: Bad symbol(s): " + chunk)
                break

    def all(self, attributes: str) -> Sheet:
        override = parse_args(attributes)

        for i in range(len(self.notes)):
            self.notes[i] = _merge_note(self.notes[i], override)

        return self

    # Like so: "s: =.5 >2"
    def tag(self, instructions: str) -> Sheet:
        parts = instructions.split(":")
        key_section = parts[0]
        info_section = ":".join(parts[1:])
        return self._tagged(key_section, info_section)

    # Print length
    def debug(self, name: str) -> Sheet:
        n = Notify()
        n.title = name 
        n.message = "Len: " + str(self.len())
        n.send()
        return self 

    def _tagged(self, tag: str, attributes: str) -> Sheet:
        override = parse_args(attributes)
        
        if tag in self.tagged_indices:
            for index in self.tagged_indices[tag]:
                self.notes[index] = _merge_note(self.notes[index], override)
        #else:
            #print("WARN: No notes available with given tag:", tag)

        return self 

    
    # Modify dots by their ordinal since last dot, e.g. [2] = "0 1 0 0 . 0 1 0 0"
    def dots(self, note_nums: list[int], attributes: str) -> Sheet:
        override = parse_args(attributes)

        for p in self.part_indices:
            for i in note_nums:
                if i < 1:
                    print("Error: note count starts at 1")
                self.notes[p + i - 1] = _merge_note(self.notes[p + i - 1], override)

        return self

    # See MetaSheet.paste() 
    def copy(self, name: str) -> Sheet:
        self.meta_sheet.clipboard[name] = copy_sheet(self)
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

if __name__ == "__main__":

    import meta_sheet as ms_lib

    meta_sheet = ms_lib.MetaSheet("", "", PostingTypes.PROSC)
    sheet = meta_sheet.sheet("0 13 4 3 . 8 6 2 1 . 0 4 22 4")

    sheet.dots([1], ">4.0")

    def attr_assert(index: int, attr: str, target: float):
        assert sheet.notes[index][attr] == target, "Wrong " + attr + ": " + str(sheet.notes[index][attr])

    attr_assert(0, "tone", 0.0)
    attr_assert(1, "tone", 13.0)
    attr_assert(10, "tone", 22.0)

    attr_assert(8, "sus", 4.0)
    attr_assert(0, "sus", 4.0)

    len_sheet = meta_sheet.sheet("0 0 0 0").all("=1.5")

    assert len_sheet.len() == 6.0, "Unexpected total res: " + str(len_sheet.len())

    assert arr_fmt([0,1,22], [0,2,0], [0,0,1,0]) == "0 1 22 . 0 2 0 . 0 0 1 0", "Bad arr_fmt: " + arr_fmt([0,1,22], [0,2,0], [0,0,1,0]) 

    mscont = ms_lib.MetaSheet("", "", PostingTypes.PROSC)
    cont_s = mscont.sheet("2 3 4 5").all("=1.0").dots([1], "=5.0")
    mscont.cont()
    assert len(mscont.sheets) == 2
    assert mscont.sheets[-1].notes[0]["reserved_time"] == 5.0
    assert mscont.sheets[-2].notes[0]["reserved_time"] == 5.0

    inline_sheet = meta_sheet.sheet("0 2[=0.5 >.5 #2]s")
    assert inline_sheet.notes[1]["reserved_time"] == 0.5, "Inline tag not applied " + str(inline_sheet.notes[1]["reserved_time"])

    # Special compile thingies 
    testcompile = compile_sheet("0 (1/2[=.5]s/3) 0 (1/2)")
    expected = "0 1 0 1 0 2[=.5]s 0 2 0 3 0 1"
    assert testcompile == expected, "String compilation failure, expected {} but got {}".format(expected, testcompile)