from new_meta_sheet import MetaSheet

class MetaSheetData:
    def __init__(self, name: str, sequencer_tag: str, meta_sheet: MetaSheet, exporter_func):
        self.exporter_func = exporter_func # See note_export.py for format (and export_all, here)
        self.name = name # TODO: Is it needed? 
        self.sequencer_tag = sequencer_tag
        self.meta_sheet = meta_sheet

class Composer:
    def __init__(self):
        self.meta_sheets = list[MetaSheetData]
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
        
        played_since_sync = [data.meta_sheet for data in self.meta_sheets if data.meta_sheet.len() > self.last_sync_time]
        
        top_length = [data.meta_sheet for data in self.meta_sheets if data.meta_sheet.len() == self.len()]
        if top_length:

            for ms in played_since_sync:
                if ms.sequencer_tag not in exclude:
                    ms.reach(self.len()) 
                else: 
                    print("excluding " + ms.sequencer_tag)

            self.sync()

        return self

    # Transform all notes in all sheets into export dicts and return as list
    def export_all(self) -> list[dict]:
        all_notes = []
        for data in self.meta_sheets:
            all_notes.append(data.exporter_func(data.meta_sheet, data.name, data.sequencer_tag))
        return all_notes