from sheet_utils import PostingType, PostingTypes, _merge_note, _parse_note, _export_note, export_nrt
from scales import *
from sheet import Sheet, copy_sheet

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
        self.new_sheet_callback = None # Changes to actual callback if set_callback() called
        
    def set_callback(self, callback):
        self.new_sheet_callback = callback

    # Create and save a new sheet 
    def sheet(self, source: str, scale: list[int] = CHROMATIC, octave: int = 0) -> Sheet:
        sheet = Sheet(self, source, scale, octave)
        self.sheets.append(sheet)
        if self.new_sheet_callback != None:
            self.new_sheet_callback()
        return sheet

    # Grab a previously copy():d sheet by name and add it to the end of sheet (returning it)
    # Note copy() - it's a copy of the copy, not the original sheet instance 
    def paste(self, clipboard_name: str) -> Sheet:
        if clipboard_name in self.clipboard:
            sheet = copy_sheet(self.clipboard[clipboard_name])
            self.sheets.append(sheet)
            return sheet

        print("ERROR: Copied sheet with name", clipboard_name, "not found")
        return Sheet(self, "")

    # Play the latest sheet again if exists 
    def cont(self, times=1) -> 'MetaSheet':
        if len(self.sheets) > 0:
            for i in range(0, times):
                self.sheets.append(copy_sheet(self.sheets[-1]))

        return self

    # Repeat latest registered sheet until total length matches <length>, padding any remains
    def reach(self, length: float) -> 'MetaSheet':
        diff = length - self.len()
        if len(self.sheets) > 0:
            latest = copy_sheet(self.sheets[-1])
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
    def pad(self, time: float) -> 'MetaSheet':
        # Bit hacky to use the native string parse method (note the *10) but it works for now...
        self.sheet("0", CHROMATIC, 0).all("#0 =" + str(time))
        return self

    # Returns total length of all sheets 
    def len(self) -> float:
        return sum([sheet.len() for sheet in self.sheets])

    # Get all notes from all sheets in order and make them sequencer-compatible
    def export_all(self) -> list[dict]:
        all_notes: list[dict[str,float]] = [note for sublist in [sheet.to_notes(self.to_hz) for sheet in self.sheets] for note in sublist]
        return [_export_note(note, self.instrument, self.sequencer_id, self.posting_type) for note in all_notes]
    
    # Same as above but for NRT PROSC posting 
    def to_nrt(self) -> list[dict]:
        all_notes: list[dict[str,float]] = [note for sublist in [sheet.to_notes(self.to_hz) for sheet in self.sheets] for note in sublist]
        return [export_nrt(note, self.instrument) for note in all_notes]


if __name__ == "__main__":
    meta_sheet = MetaSheet("sequencer_id", "instrument", PostingTypes.PROSC)
    meta_sheet.sheet("0 0 0 0")
    meta_sheet.len()
    meta_sheet.pad(4.0)