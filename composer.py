from meta_sheet import MetaSheet
import zmq_client

# Helper class for managing multiple MetaSheets. Plays the role of a "timeline" in composition as 
# well as main UI for quickly changing large parts of the composition (e.g. mute everything)
# All metaSheets added via reg() are affected by composer calls. 
class Composer:
    def __init__(self) -> None:
        self.meta_sheets: list[MetaSheet] = []
        self.client = zmq_client.PublisherClient()
        self.last_sync_time = 0.0
        self.restart_sheet_indices: dict[str, int] = {}
        # Tags for sheets, triggered on sync 
        self.pre_tagged: list[str] = []


    def reg(self, meta_sheet: MetaSheet) -> MetaSheet:
        self.meta_sheets.append(meta_sheet)
        meta_sheet.set_callback(self.tag_all)
        return meta_sheet
    
    # Pad all sheets with silence until everything is the same length 
    def sync(self) -> 'Composer':
        for meta_sheet in self.meta_sheets:
            diff = self.len() - meta_sheet.len()
            if diff > 0.0:
                meta_sheet.pad(diff)

        self.last_sync_time = self.len()
        return self 

    def cont(self, mss: list[MetaSheet]) -> 'Composer':
        for ms in mss:
            ms.cont()

        return self

    # Convenience call to be placed in the middle of active compositions 
    # See usage of restart indices in post_all; effectively says not to play anything up until this point
    def restart(self) -> 'Composer':
        for ms in self.meta_sheets:
            if len(ms.sheets) > 0:
                self.restart_sheet_indices[ms.sequencer_id] = len(ms.sheets)

        return self

    def pre_tag(self, tag: str) -> 'Composer': 
        self.pre_tagged.append(tag)
        return self 

    def tag_all(self) -> 'Composer':
        for meta_sheet in self.meta_sheets:
            for sheet in meta_sheet.sheets:
                for tag in self.pre_tagged:
                    sheet.tag(tag)

        return self

    def debug(self) -> 'Composer':
        for meta_sheet in self.meta_sheets:
            for sheet in meta_sheet.sheets:
                if sheet.debug_mark != "":                
                    sheet.debug(sheet.debug_mark)

        return self 

    # Detects which sheets were played since last sync() call and repeats 
    # those to match the longest one (i.e. "play and repeat together")
    def smart_sync(self, exclude: list[MetaSheet]=[]) -> 'Composer':

        # Make sure tagged values are up to date
        self.tag_all()
        
        played_since_sync = [meta_sheet for meta_sheet in self.meta_sheets if meta_sheet.len() > self.last_sync_time]
        
        top_length = [ms for ms in self.meta_sheets if ms.len() == self.len()]
        if top_length:
            
            ex_alias = [ms.sequencer_id for ms in exclude]

            for ms in played_since_sync:
                if ms.sequencer_id not in ex_alias:
                    ms.reach(self.len()) 
                else: 
                    print("excluding " + ms.sequencer_id)

            self.sync()

            print("AFTER SYNC: " + str(self.len()))
            for note_set in [ms.sequencer_id + str(ms.sheets[-1].notes) for ms in self.meta_sheets if len(ms.sheets) > 0]:
                print("   - " + note_set)

        return self 

    # Return the end point of the composer timeline; the length of the longest contained metasheet 
    def len(self) -> float:
        return max([ms.len() for ms in self.meta_sheets]) if self.meta_sheets != [] else 0.0

    # Post export and post everything to jdw-sequencer 
    def post_all(self):
        for meta_sheet in self.meta_sheets:

            if meta_sheet.sequencer_id in self.restart_sheet_indices:
                meta_sheet.sheets = meta_sheet.sheets[self.restart_sheet_indices[meta_sheet.sequencer_id]:]

            self.client.queue(meta_sheet.export_all())

if __name__ == "__main__":
    cmp = Composer()
    cmp.pre_tag("s:=.5")
    cmp.restart()
    cmp.smart_sync()
    cmp.sync()
    cmp.tag_all()