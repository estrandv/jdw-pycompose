import parsing
from copy import deepcopy
from sheet_note import SheetNote

class Sheet:
    def __init__(self, source_string: str):
        self.notes: list[SheetNote] = parsing.parse_sheet(source_string)
    
    # e.g. "=1.5 >2"
    def all(self, attributes: str) -> 'Sheet':
        override = parsing.parse_args(attributes)

        for note in self.notes:
            for arg in override:
                note.set_arg(arg, override[arg])

        return self

    # Like so: "s: =.5 >2" will set provided attributes to all notes prefixed "s"
    def tag(self, instructions: str) -> 'Sheet':
        parts = instructions.split(":")
        key_section = parts[0]
        info_section = "".join(parts[1:])

        args = parsing.parse_args(info_section)

        tag = key_section
        for note in self.notes:
            for arg in args:
                if note.suffix == tag:
                    note.set_arg(arg, args[arg])

        return self 

    # Double own notes <times> amount of times
    def stretch(self, times: int = 1) -> 'Sheet':
        appenders = deepcopy(self.notes)

        for _ in range(0, times):
            self.notes += appenders
        return self
    
    # Add notes as if adding a new sheet, but included in the current one 
    def extend(self, source_string: str) -> 'Sheet':
        self.notes += parsing.parse_sheet(source_string)
        return self 

    # Define the same sheet again, adding the new notes to the previous one from the start of the timeline
    def para(self, source_string: str) -> 'Sheet':
        new_notes = parsing.parse_sheet(source_string)
        original_step = [note.get_time() for note in self.notes]

        # [0.0, 0.5, 1.0, 2.0]
        # [0.5, 0.5, 2.0, 2.5]
        # 1. For each NEW_NOTE, determine its relative value
        # 2. Find the first relative original time that is equal or lesser than the NEW_NOTE rel time 
        # 3. Set NEW_NOTE time (absolute? best fit for writing?) to the diff (e.g. 0.2 > than the og rel time = 0.2)
        #   - Regarding which time arg to use:
        #   * sheet("1 2 3").para("0 2").all("=2")
        #   * In this case the para notes should NOT get the ALL arg 
        #   * Problem is that sometimes you might want to apply ALL to para before any funkiness
        #   * Best way is probably to supply a baked in all_string, possibly also a tag_string (which means tag rework TODO)
        # 4. Inject the new note right after the old note using index search..? 
        #   - Another way is to use a custom object with relative times and notes
        #   - Thus you have an original set of those and keep adding at the end
        #   - Then you perform a custom sort and create the final note set 

        # Construct the relative start times of the original notes 
        timeline = 0.0
        rot = []
        for time in original_step:
            rot.append(timeline)
            timeline += time 

        new_timeline = 0.0
        for note in new_notes:
            # new_timeline is the note start time 
            # Add note to new timeline time at end after checks 
            print("UNIMPLEMENTED")
        
        # TODO: Very much not done 
        return self 


    def mute(self) -> 'Sheet':
        self.notes = []
        return self 

    def len(self) -> float:
        return sum([note.get_time() for note in self.notes]) if len(self.notes) > 0 else 0.0

if __name__ == "__main__":
    sheet = Sheet("0tag 0 0[=2]tagz 0").all("=4").tag("tag:=3")

    assert 3.0 == sheet.notes[0].get_time(), sheet.notes[0].__dict__
    assert 4.0 == sheet.notes[1].get_time(), sheet.notes[0].__dict__
    assert 2.0 == sheet.notes[2].get_time(), sheet.notes[0].__dict__
    assert 4.0 == sheet.notes[3].get_time(), sheet.notes[0].__dict__

    assert 13.0 == sheet.len(), sheet.len()
    sheet.stretch(1)
    assert 26.0 == sheet.len(), sheet.len()
