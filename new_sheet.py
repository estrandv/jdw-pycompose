import parsing
from copy import deepcopy
from sheet_note import SheetNote

ARG_NORMAL = 0
ARG_REL = 1
ARG_MUL = 2

class Sheet:
    def __init__(self, source_string: str, predefined: list[SheetNote] = []):
        if source_string != None:
            self.notes: list[SheetNote] = parsing.parse_sheet(source_string)
        else: # Alternative constructor 
            self.notes = predefined

    def __deepcopy__(self, memo):
        new_notes = [deepcopy(note) for note in self.notes]
        return Sheet(None, new_notes)
    
    # e.g. "=1.5 >2"
    def all(self, attributes: str, type = ARG_NORMAL) -> 'Sheet':
        override = parsing.parse_args(attributes)

        for note in self.notes:
            for arg in override:
                if type == ARG_NORMAL:
                    note.set_arg(arg, override[arg])
                if type == ARG_REL:
                    note.set_relative(arg, override[arg])
                if type == ARG_MUL:
                    note.set_mul(arg, override[arg])

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

    # Adjust the given arg for each note in order by applying add/subtract of amount based on pattern
    def shape(self, pattern: list[int], arg: str, amount: float) -> 'Sheet':
        old_total = self.get_total(arg)
        index = 0
        for note in self.notes:
            if pattern[index % len(pattern)] > 0:
                note.set_relative(arg, amount)
            else:
                note.set_relative(arg, amount * -1.0)

            index += 1

        diff = (old_total - self.get_total(arg))

        split_diff = diff / len(self.notes)

        for note in self.notes:
            note.set_relative(arg, split_diff)

        return self 


    def get_total(self, arg_name: str) -> float:
        return sum([(note.get_args()[arg_name] if arg_name in note.get_args() else 0.0) for note in self.notes])

    # Define the same sheet again, adding the new notes to the previous one from the start of the timeline
    def para(self, source_string: str) -> 'Sheet':
        new_notes = parsing.parse_sheet(source_string)

        # 
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
        
        # Dynamic since we will live-insert into original_step 
        def get_rot():
            timeline = 0.0
            rot = [timeline]
            for note in self.notes:
                rot.append(timeline)
                timeline += note.get_time() 
            return rot


        new_timeline = 0.0
        for note in new_notes:
            relative_time = new_timeline
            new_timeline += note.get_time()

            # Highest original relative time that is lesser than or equal to this 
            original_index = 0 # Iteration index in self.notes 
            highest_candidate = 0.0 # Highest matching relative time in self.notes
            selected_index = 0 # Candidate index in self.notes
            for time in get_rot():
                if time <= relative_time:
                    highest_candidate = time
                    selected_index = original_index
                original_index += 1
            
            print("Selected index at", selected_index, "with value", highest_candidate, "timeline now", new_timeline)

            # Zero, unless times don't match 
            diff = abs(relative_time - highest_candidate)

            # If there is no diff, we set the new note time to zero, absorbing it into the old one
            # (it is thus important that it is later placed BEFORE the old note)
            note.set_master_arg("time", 0.0)


            if diff == 0.0:
                self.notes.insert(selected_index - 1, note)
            # If not, we reduce the old note by diff and then place the new note AFTER the old note 
            else:
                # TODO: This part isn't really working 
                self.notes[selected_index].set_master_arg("time", self.notes[selected_index].get_time() - diff)
                print("Adjusting", diff, "to", self.notes[selected_index].get_time())
                self.notes.insert(selected_index, note)

        print([note.get_time() for note in self.notes])
        
        return self 


    def mute(self) -> 'Sheet':
        self.notes = []
        return self 

    def is_quiet(self) -> bool:
        retval = True 
        for note in self.notes:
            if note.get_args()["amp"] > 0.0:
                retval = False 
        return retval

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

    # Smart mod 
    sheet2 = Sheet("1 2 3 4 5 6 7 8").shape([1,0], "time", 0.2)

    assert sheet2.len() == 8.0, sheet2.len()
    assert sheet2.notes[0].get_args()["time"] == 1.2, sheet2.notes[2].get_args()["time"] 
    assert sheet2.notes[1].get_args()["time"] == 0.8, sheet2.notes[2].get_args()["time"] 

    sheet3 = Sheet("1 2 3 4 5").shape([1,0,0], "amp", 0.2)
    assert sheet3.notes[3].get_args()["amp"] == 1.24, sheet3.notes[3].get_args()["amp"] 

    sheet4 = Sheet("0 0 0 0 0 0 0 0").all("=2", ARG_REL)
    assert sheet4.len() == 8 * 3

    sheet5 = Sheet("1[||=0.5] 2 3 4").all("=4")
    assert sheet5.len() == 14.0

    sheet6 = Sheet("0 0 0 2 4 (5/1) _ 0").all(">0.5 #0.2").all("sus2.5", ARG_REL)
    assert sheet6.notes[0].get_args()["sus"] == 3.0, sheet6.notes[0].get_args()["sus"] == 3.0