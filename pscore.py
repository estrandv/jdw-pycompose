# Attempt at rethinking composition as programmatical

### Attributes 
# Tone: The most commonly changed. Integer in scale, unnamed?
# Reserved Time: Keeping track of "4/4" can be tricky, but newline builder pattern is one way. 
# Sus/Amp: Little special handling needed, but since they are expected they are the bare minimum defaults (along with tone and res).

### K/V typing
# note({"amp": 0.4, "tone": 3}) is the most free-form way, but typing out quoted attribute names is a bit wonky. 
# note(4, amp=0.4, custom={"rate": 0.4}) might be the closest we get to ergonomic free-form.
#   - this way we can enforce defaults for the syntax-required values while also allowing free-type in the same call. 

### Meta-Attributes
# Scale, Octave, Transposition
# Should probably be args for section(). If it gets repetitive we can re-evaluate. 

### Structure
# Things like reach() should now go in section()
# Calls like sync() however are trickier. Should padding silence implicitly be part of the last section, or part of its own? 
#   - If I call score.section().note(3), then sync(), then score.last_section() - what does it play? 
#   - I'd argue you expect it to just play note(3) without any extra silence. 
#   - This means we can contain all notes in sections, but we might have to define rules for what cosntitutes "last section"
#   - So while score.pad() should create a new section with a silent note that doesn't count as "last section", section.pad() should just add notes in there.
# There's also the reach() statement. If you do note().note().reach().note() it should likely mean "Play these two until, then play this once".
#   - Calling score.section() should implicitly save the last section, but sometimes you might want to manually end a section early. 
#   - score.section().note().note().reach(16.0).end().section().note().note().reach(16.0)
#   - end() would return the underlying score object. 
#   - However sometimes you might want to combine sections. This could be done in different ways. 
#       a. score.last_section(2) would create a combined section of the last two sections.
#       b. section.into() would treat the sections as separate while typing but then merge them into one in the score
#       c. score.save(2, "bonkers") would register the last two sections with the id while score.load("bonkers") would repeat them
# Of these, I think both a and c and needed for different scenarios. B however might be a bit tacked-on and hard to exectue. 
#   - Might still be nice to try and do B as well since being able to execute that means we have a robust architecture 
#
from __future__ import annotations
from copy import deepcopy
from scales import MAJOR, transpose

from pretty_midi.utilities import note_number_to_hz

# Transform the local note dict into the api expected format 
# TODO: name/value should probably be renamed to key/value
# name/value format is needed to work with the strict typing requirements of the current
# sequencer Rust JSON API. 
def _export_note(note: dict[str, float], synth_name: str):
    exported = {"synth": synth_name, "values": []}

    for key in note:

        # TODO: Dirty hack until harmonized
        if key == "tone":
            val = {"name": "freq", "value": note["tone"]}
        else:
            val = {"name": key, "value": note[key]}
        exported["values"].append(val)

    return exported


class Score:
    def __init__(self):
        self.sections: list[Section] = []
        self.saved_sections: dict[str, list[Section]] = {}


    def len(self) -> float:
        total = 0.0
        for l in [sec.len() for sec in self.sections]:
            total += l
        return total

    def pad(self, beats) -> Score:
        new = Section(self)
        new.pad(beats)
        self.sections.append(new)
        return self

    def mute(self) -> Score:
        self.sections = []
        return self 

    def repeat_last(self, times=1) -> Score:

        for i in range(0, times):
            self.sections.append(deepcopy(self.last_section))
        return self 

    def section(self) -> Section:
        section = Section(self)
        self.sections.append(section)
        section.defaults["amp"] = 1.0
        section.defaults["sus"] = 1.0
        section.defaults["reserved_time"] = 1.0
        self.last_section = section
        return section

    def save_last(self, name, steps_back = 1) -> Score:
        print("Unimplemented")
        return self 

    def repeat(self, saved_name) -> Score:
        print("Unimplemented")
        return self 

    def export(self, synth_name: str) -> list:
        
        exported = []
        for section in self.sections:
            for note in section.notes:
                exported.append(_export_note(note, synth_name))

        return exported
    
    def illustrate(self) -> str:
        return str([section.illustrate() for section in self.sections])

class Section:

    # Class itself should have only noargs constructor
    def __init__(self, parent: Score):
        self.notes: list[dict[str, float]] = []
        self.defaults: dict[str, float] = {"amp": 1.0, "sus": 1.0, "reserved_time": 1.0} # Super basic "avoid-null-errors" defaults; expected to be overwritten
        self.parent: Score = parent
        self.scale: list[int] = MAJOR
        self.octave: int = 4

    # Selectively override defaults with only the specified values 
    def def_ovr(self, custom: dict[str, float]) -> Section:
        for key in custom:
            self.defaults[key] = custom[key]
        return self

    def in_scale(self, scale: list[int]) -> Section:
        self.scale = scale 
        return self

    def in_octave(self, octave: int) -> Section:
        self.octave = octave
        return self

    def _default_fallback(self, values: dict) -> dict[str, float]:
        
        processed: dict[str,float] = {}

        for key in self.defaults:
            if key not in values or values[key] == None:
                if key in self.defaults:
                    processed[key] = float(self.defaults[key])

        for key in values:
            if values[key] != None:
                processed[key] = values[key]

        return processed

    # Add a note to the end of the section. Values not provided will fall back on the last specified dynamic defaults.
    # Use the "custom" arg to provide a free-form list of key/value attributes when the defaults are not enough.
    def hz_note(self, hz_freq: float, amp: float = None, sus: float = None, res: float = None, default_set: bool = False, custom: dict[str, float] = {}) -> Section:

        new_note: dict = {"tone": hz_freq, "amp": amp, "sus": sus, "reserved_time": res}

        # Override everything by name from custom
        for field in custom:
            if field in custom and custom[field] != None:
                new_note[field] = custom[field]

        default_fallback = self._default_fallback(new_note)

        if default_set:
            self.defaults = default_fallback

        self.notes.append(default_fallback)
        return self

    # Repeat the last note again, but with the specified values overridden
    def next(self, custom: dict[str, float]) -> Section:
        if self.notes:
            last = deepcopy(self.notes[-1])
            for key in custom:
                last[key] = custom[key]

            self.notes.append(last)

        return self

    # Play the last note <steps> amount of times, interpolating the given properties 
    # towards their respective values in <steps> amount of equal increments 
    def interpolate(self, properties: dict[str, float], steps: int) -> Section:
        last_note = self.defaults
        if self.notes:
            last_note = self.notes[-1]

        step_map = {}
        for key in properties:
            start = 0.0
            if key in last_note:
                start = last_note[key]
            diff = properties[key] - start 
            step = diff / steps
            step_map[key] = step

        for i in range(0, steps):
            new_note = self.defaults
            if self.notes:
                new_note = deepcopy(self.notes[-1])
            for key in step_map:
                if key not in new_note:
                    new_note[key] = 0.0
                new_note[key] += step_map[key]
            self.notes.append(new_note)

        return self
                    
    # Alternative implementation of the above with auto-scaled midi index as tone arg
    # Mostly ergonimics
    def note(self, midi_tone: int, amp: float = None, sus: float = None, res: float = None, default_set: bool = False, custom: dict[str, float] = {}) -> Section:
        hz_tone = note_number_to_hz(self._midi_format(midi_tone))
        return self.hz_note(hz_tone, amp, sus, res, default_set, custom)

    # Ergonomy / Readability implementation of note attribute typing 
    # See parsing.py 
    def txt(self, note_string: str) -> Section:
        from parsing import parse_note
        
        note = parse_note(note_string)

        tone = note["tone"]
        hz_tone = note_number_to_hz(tone)
        note["tone"] = hz_tone

        default_fallback = self._default_fallback(note)

        self.notes.append(default_fallback)

        return self 
        

    def _midi_format(self, midi_tone: int) -> int:

        extra = 0
        if self.octave > 0:
            extra = (12 * (self.octave - 1))

        ocatave_tone = extra + midi_tone
        transposed_tone = transpose(ocatave_tone, self.scale)
        return transposed_tone

    # Play last registered note <times> amount of times - x(1) effectively does nothing 
    def x(self, times: int) -> Section:
        if len(self.notes) > 0:
            last_note = self.notes[-1]
            
            if times > 1:
                times = times - 1
                for i in range(0, times):
                    self.notes.append(deepcopy(last_note)) 

        return self

    # Be silent for <time> amount of beats 
    def pad(self, time: float) -> Section:
        # TODO: Might have to pad with more values AND be careful regarding things like transpose or scale 
        self.notes.append({"amp": 0.0, "reserved_time": time})

        return self

    # Returns the total reserved time of the section
    def len(self) -> float:
        total = 0.0
        for l in [note["reserved_time"] for note in self.notes]:
            total += l
        return total

    # Absorb all the notes from another section
    def append(self, other: Section) -> Section:
        for note in other.notes:
            self.notes.append(deepcopy(note))
        return self

    # Repeat the notes so far until the wrapping score reaches a total beat length of... 
    def until_total(self, beats) -> Section:

        sample: Section = Section(self.parent)
        sample.notes = deepcopy(self.notes)
        
        while self.parent.len() < beats:
            diff = beats - self.parent.len()
            if sample.len() <= diff:
                self.append(sample)    
            else:
                self.pad(diff)
                break

        return self

    # Repeat the notes so far until the beat length of...
    def until(self, beats) -> Section:

        sample: Section = Section(self.parent)
        sample.notes = deepcopy(self.notes)

        while self.len() < beats:
            diff = beats - self.len()
            if sample.len() <= diff:
                self.append(sample)
            else:
                self.pad(diff)
                break

        return self

    # Ergonomic way to end section processing and return to parent
    def end(self) -> Score:
        return self.parent

    def illustrate(self) -> str:
        return str([note["amp"] for note in self.notes])


def test():
    sco = Score() 
    sec = sco.section()
    sec.defaults["reserved_time"] = 1.0
    sec.hz_note(1.0).hz_note(2.0).until(4.0)
    assert len(sec.notes) == 4, "Expected len 4, got " + str(len(sec.notes))
    sec.until_total(16.0)
    assert len(sec.notes) == 16, "Expected len 16, got " + str(len(sec.notes))
    assert sec.notes[15]["tone"] == 2.0, "Expected tone 2.0 for last note, got: " + str(sec.notes[15]["tone"]) 
    assert sec.notes[14]["tone"] == 1.0, "Expected tone 1.0 for second last note, got: " + str(sec.notes[14]["tone"]) 

    sec2 = sco.section().hz_note(4.0).x(4).pad(3.0)
    assert len(sec2.notes) == 5, "Expected 4 notes and one silent note, got: " + str(len(sec2.notes))
    assert sec2.notes[3]["tone"] == 4.0, "Expected second last tone to be 4.0, got: " + str(sec2.notes[3]["tone"])
    assert sec2.notes[4]["amp"] == 0.0, "Expected last note to be silence"
    assert sec2.notes[4]["reserved_time"] == 3.0, "Expected last note to be the full padded silence amount of 3.0, got: " + str(sec2.notes[4]["reserved_time"])

    sec3 = sco.section()
    sec3.defaults["amp"] = 0.3
    sec3.note(1)
    assert sec3.notes[0]["amp"] == 0.3, "Expected default of 0.3 applied to amp, got: " + str(sec3.notes[0]["amp"])

    # Export testing 
    note = sco.section().hz_note(9.0).notes[0]
    exported = _export_note(note, "banana")
    assert {"name": "freq", "value": 9.0} in exported["values"]
    assert exported["synth"] == "banana"

    # Parse testing 
    note = sco.section().txt("11 res10 sus15 amp20").notes[0]
    assert note["sus"] == 1.5
    assert note["amp"] == 2.0
    assert note["reserved_time"] == 1.0

    # TODO: Tests for transpose, midi-to-hz, scaling...


if __name__ == "__main__":
    print("Script called directly, running tests...")
    test()
    print(">> All tests ok!")



