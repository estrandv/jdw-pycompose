from new_meta_sheet import MetaSheet
from note_export import de_wrap

class MetaSheetData:
    def __init__(self, name: str, sequencer_tag: str, meta_sheet: MetaSheet, exporter_func):
        self.exporter_func = exporter_func # See note_export.py for format (and export_all, here)
        self.name = name # TODO: Is it needed? 
        self.sequencer_tag = sequencer_tag
        self.meta_sheet = meta_sheet

class Composer:
    def __init__(self):
        self.meta_sheets: list[MetaSheetData] = [] 
        self.last_sync_time = 0.0

    def meta_sheet(self, name: str, sequencer_tag: str, exporter_func) -> MetaSheet:
        new_meta = MetaSheet()
        self.meta_sheets.append(MetaSheetData(name, sequencer_tag, new_meta, exporter_func))
        return new_meta

    # Return the end point of the composer timeline; the length of the longest contained metasheet 
    def len(self) -> float:
        return max([data.meta_sheet.len() for data in self.meta_sheets]) if self.meta_sheets != [] else 0.0

    # Pad all sheets with silence until everything is the same length 
    def sync(self) -> 'Composer':
        for data in self.meta_sheets:
            diff = self.len() - data.meta_sheet.len()
            if diff > 0.0:
                data.meta_sheet.pad(diff)

        self.last_sync_time = self.len()
        return self 

    # Detects which sheets were played since last sync() call and repeats 
    # those to match the longest one (i.e. "play and repeat together")
    def smart_sync(self, exclude: list[str]=[]) -> 'Composer':

        # TODO: Activate/Deactivate for meta-sheets
        # 1. Meta-sheets should keep track of latest non-silent sheets 
        #   - Needs some kind of tag for sheet() and reach() to register latest live sheet
        #   - REach should then play this instead 
        # 2. Meta-sheets should be able to wipe all registered sheets
        #   - Should be doable to register a latest for syncing while having wiped previously added 
        # 3. played_since_sync should require sheets to be active() when searching
        #   - Calling wipe() should deactivate 
        #   - Calling sheet() should automatically activate 
        #   - ... or we just add OR is_active to this check and let the len() arg work as before 
        played_since_sync = [data for data in self.meta_sheets if data.meta_sheet.len() > self.last_sync_time]
        
        # Verify that at least one sheet exists with the total len() - TODO: Why was this added?
        #top_length = [data.meta_sheet for data in self.meta_sheets if data.meta_sheet.len() == self.len()]
        #if top_length:
        for ms in played_since_sync:
            if ms.sequencer_tag not in exclude:
                ms.meta_sheet.reach(self.len()) 
            else: 
                print("excluding " + ms.sequencer_tag)

        self.sync()

        return self

    def wipe(self):
        for ms in self.meta_sheets:
            ms.meta_sheet.wipe()

    # Transform all notes in all sheets into export dicts and return as list
    def export_all(self) -> list[dict]:
        all_notes = []
        for data in self.meta_sheets:
            # Don't export all-silent meta-sheets 
            if not data.meta_sheet.is_silent():
                all_notes.append(data.exporter_func(data.meta_sheet, data.name, data.sequencer_tag))
        return all_notes

    # Fetch all explicit "this should be muted" messages for empty/silent meta sheets 
    def export_wipe_aliases(self) -> list[dict]:
        return [data.sequencer_tag for data in self.meta_sheets if data.meta_sheet.is_silent()]

    def nrt_export(self, sequencer_tag: str) -> list[dict]:
        ms = [ms for ms in self.meta_sheets if ms.sequencer_tag == sequencer_tag][0]

        notes = ms.exporter_func(ms.meta_sheet, ms.name, ms.sequencer_tag)
        dw = de_wrap(notes)

        return dw 

if __name__ == "__main__":
    exported = []
    
    def test_exp(sheet, name, tag):
        exported.append(name)
    
    cmp = Composer()
    msh = cmp.meta_sheet("flute", "fl1", test_exp)
    msh.sheet("0 0 0 0")
    assert 4.0 == cmp.len(), cmp.len()
    msh2 = cmp.meta_sheet("strings", "st1", test_exp)
    msh2.sheet("0 0 0 0 0")
    assert 5.0 == cmp.len(), cmp.len()
    cmp.sync()
    assert 5.0 == msh.len()
    assert 0.0 == msh.sheets[-1].sheet.notes[0].get_args()["amp"]
    msh.sheet("1 1 0 0")
    msh2.sheet("4")
    cmp.smart_sync()
    assert 9.0 == msh2.len()
    assert 1.0 == msh2.sheets[-1].sheet.len()
    assert 1.0 == msh2.sheets[-1].sheet.notes[0].get_args()["amp"]


    ncmp = Composer()
    ms1 = ncmp.meta_sheet("flute", "flute", test_exp)
    ms1.sheet("0 _ _ 3 4 5 _ _")
    ms2 = ncmp.meta_sheet("vio", "vo", test_exp)
    ms2.sheet("bd3 _ _ _ bd2 _ _ _ bd7 _ sh4 _ _ hh1 hh2 _").all("=0.25")
    assert 4.0 == ms2.len(), ms2.len()
    assert 8.0 == ms1.len(), ms1.len()
    ncmp.smart_sync()
    assert 8.0 == ncmp.len(), ncmp.len()
    assert 8.0 == ms1.len(), ms1.len()
    assert 8.0 == ms2.len(), ms2.len()

    def test_nrt(sheet, name):
        exported.append(name)

    #cmp.nrt_export("flute")