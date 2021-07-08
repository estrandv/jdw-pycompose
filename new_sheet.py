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
    def stretch(self, times: int) -> 'Sheet':
        appenders = deepcopy(self.notes)

        for _ in range(0, times):
            self.notes += appenders
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
