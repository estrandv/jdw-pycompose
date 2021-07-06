from sheet_note import SheetNote

# WIP

# MIDI_EVENT: {"target": "nintendo", "type": "NOTE_ON", "args": [...]}
# SAMPLE_PLAY: {"target": "dr660", "family": "BASS(0)", "index": 4, "args": {...}}
# S_NEW: {"target": "moog", "args": {...}}

def to_synth_note(note: SheetNote, target: str) -> dict[str, any]:

    # TODO: Amp, Freq (and transpose), Time, Sequencer wrap... 

    synth_note = {"target": target, "args": note.get_args()}
    
    return synth_note