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

class Score:
    def __init__(self):
        self.sections: list[Section] = []

    def len(self) -> float:
        total = 0.0
        for l in [sec.len() for sec in self.sections]:
            total += l
        return total

    def section(self) -> Section:
        section = Section(self)
        self.sections.append(section)
        section.defaults["amp"] = 1.0
        section.defaults["sus"] = 1.0
        section.defaults["res"] = 1.0
        return section

class Section:

    # Class itself should have only noargs constructor
    def __init__(self, parent: Score):
        self.notes: list[dict[str, float]] = []
        self.defaults: dict[str, float] = {}
        self.parent: Score = parent

    def note(self, tone: int, amp: float = None, sus: float = None, res: float = None, custom: dict[str, float] = {}) -> Section:

        # Set any non-assigned vars as dynamic defaults 
        def default_set(value, name: str):
            if value == None:
                return self.defaults[name]
            else:
                return value

        amp = default_set(amp, "amp")
        sus = default_set(sus, "sus")
        res = default_set(res, "res")

        new_note: dict[str, float] = {"tone": float(tone), "amp": amp, "sus": sus, "reserved_time": res}

        # Override everything by name from custom
        for field in custom:
            new_note[field] = custom[field]


        self.notes.append(new_note)
        return self

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


def test():
    sco = Score() 
    sec = sco.section()
    sec.defaults["res"] = 1.0
    sec.note(1).note(2).until(4.0)
    assert len(sec.notes) == 4, "Expected len 4, got " + str(len(sec.notes))
    sec.until_total(16.0)
    assert len(sec.notes) == 16, "Expected len 16, got " + str(len(sec.notes))
    assert sec.notes[15]["tone"] == 2.0, "Expected tone 2.0 for last note, got: " + str(sec.notes[15]["tone"]) 
    assert sec.notes[14]["tone"] == 1.0, "Expected tone 1.0 for second last note, got: " + str(sec.notes[14]["tone"]) 

    sec2 = sco.section().note(4).x(4).pad(3.0)
    assert len(sec2.notes) == 5, "Expected 4 notes and one silent note, got: " + str(len(sec2.notes))
    assert sec2.notes[3]["tone"] == 4.0, "Expected second last tone to be 4.0, got: " + str(sec2.notes[3]["tone"])
    assert sec2.notes[4]["amp"] == 0.0, "Expected last note to be silence"
    assert sec2.notes[4]["reserved_time"] == 3.0, "Expected last note to be the full padded silence amount of 3.0, got: " + str(sec2.notes[4]["reserved_time"])

    sec3 = sco.section()
    sec3.defaults["amp"] = 0.3
    sec3.note(1)
    assert sec3.notes[0]["amp"] == 0.3, "Expected default of 0.3 applied to amp, got: " + str(sec3.notes[0]["amp"])


print("Script called directly, running tests...")
test()
print(">> All tests ok!")



