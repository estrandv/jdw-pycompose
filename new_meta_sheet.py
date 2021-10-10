from new_sheet import Sheet
from scales import *
from copy import deepcopy
from sheet_note import SheetNote

class SheetData:
    def __init__(self, sheet: Sheet, octave: int, scale: list[int]):
        self.sheet = sheet 
        self.octave = octave
        self.scale = scale

class MetaSheet:
    def __init__(self):
        self.sheets: list[SheetData] = []

    def wipe(self):
        self.sheets = []

    def mix(self, arg_string: str, mode = 2):
        for sheet in self.sheets:
            sheet.sheet.all(arg_string, mode) #ARG MUL 

    # Returns total length of all sheets 
    def len(self) -> float:
        return sum([data.sheet.len() for data in self.sheets])

    def sheet(self, source_string: str, octave: int = 0, scale: list[int] = CHROMATIC) -> Sheet:
        self.sheets.append(SheetData(Sheet(source_string), octave, scale))
        return self.sheets[-1].sheet

    def pad(self, time: float) -> 'MetaSheet':
        self.sheet("0[=" + str(time) + " amp0]")
        return self

    def is_silent(self) -> bool:
        reval = True 
        for sheet_data in self.sheets:
            if not sheet_data.sheet.is_quiet():
                reval = False 
        return reval

    # Repeat latest registered sheet until total length matches <length>, padding any remains
    def reach(self, length: float) -> 'MetaSheet':
        diff = length - self.len()
        if len(self.sheets) > 0:
            latest_data = deepcopy(self.sheets[-1])
            if latest_data.sheet.len() <= diff:
                self.sheets.append(latest_data)
            elif diff > 0.0:
                self.pad(diff)
            if self.len() < length:
                return self.reach(length)

        elif diff > 0.0:
            self.pad(diff)

        return self

if __name__ == "__main__":
    meta = MetaSheet()
    meta.sheet("0[=2]")
    assert 2.0 == meta.sheets[-1].sheet.len()
    meta.pad(6.0)
    assert 6.0 == meta.sheets[-1].sheet.len()
    meta.reach(14.0)
    assert 6.0 == meta.sheets[-1].sheet.len(), meta.sheets[-1].sheet.len()
    meta.reach(16.0)
    assert 2.0 == meta.sheets[-1].sheet.len(), meta.sheets[-1].sheet.len()
    assert 16.0 == meta.len()