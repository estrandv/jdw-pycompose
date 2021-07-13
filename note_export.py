from sheet_note import SheetNote
from new_meta_sheet import MetaSheet
from copy import deepcopy
from scales import transpose
from pretty_midi import note_number_to_hz
import json 

# WIP

# TODO: Monophonic synth note 
# - external_id for prosc to keep track 
# - gate=0 included in args 

# TODO: MIDI distinction
# - EVENT vs NOTE 
# - Events could rely on certain prefixes, like "pitchBend44[=2]"
# - One could even assume NOTE_ON for missing prefixes and work from that 
# - Some kind of standard could be determined from available message types: https://www.midi.org/specifications-old/item/table-1-summary-of-midi-message
# - Midi messages have arbitrary "args" just like OSC: "afterTouch8[pressure4]"

# MIDI_EVENT: {"target": "nintendo", "type": "NOTE_ON", "args": [...]}
# SAMPLE_PLAY: {"target": "dr660", "family": "BASS(0)", "index": 4, "args": {...}}
# S_NEW: {"target": "moog", "args": {...}}

def _sequencer_wrap(alias: str, time: float, msg_handle: str, msg: str) -> dict:
    return {"alias": alias, "time": time, "msg": msg_handle + "::" + msg}
 
def to_sequencer_midi_notes(meta_sheet: MetaSheet, target: str, sequencer_tag: str) -> dict:
    return {} # TODO 

def to_sample_notes(meta_sheet: MetaSheet, target: str) -> list[dict]:
    notes = []
    for data in meta_sheet.sheets:
        for note in data.sheet.notes:
            octave_tone = note.get_tone_in_oct(data.octave)
            transposed_tone: int = transpose(int(octave_tone), data.scale)
            notes.append({"target": target, "family": note.prefix, "index": transposed_tone, "args": note.get_args()})

    return notes

def to_sequencer_sample_notes(meta_sheet: MetaSheet, target: str, sequencer_tag: str) -> list[dict]:
    return [_sequencer_wrap(sequencer_tag, msg["args"]["time"], "JDW.PLAY.SAMPLE", json.dumps(msg)) \
        for msg in to_sample_notes(meta_sheet, target)]

def to_sequencer_synth_notes(meta_sheet: MetaSheet, target: str, sequencer_tag: str) -> list[dict]:
    return [_sequencer_wrap(sequencer_tag, msg["args"]["time"], "JDW.PLAY.NOTE", json.dumps(msg)) \
        for msg in to_synth_notes(meta_sheet, target)]

def to_synth_notes(meta_sheet: MetaSheet, target: str) -> list[dict]:
    notes = []
    for data in meta_sheet.sheets:
        for note in data.sheet.notes:
            octave_tone = note.get_tone_in_oct(data.octave)
            transposed_tone = transpose(int(octave_tone), data.scale)
            tone_frequency = note_number_to_hz(transposed_tone)
            note.set_arg("freq", tone_frequency)
            notes.append({"target": target, "args": note.get_args()})
    return notes 

if __name__ == "__main__":

    def decode(msg: str) -> dict:
        return json.loads("".join(msg.split("::")[1:]))

    ms = MetaSheet()
    ms.sheet("0 1 2 3", 4)
    res = to_sequencer_synth_notes(ms, "flute", "flute1")

    # CHROMATIC: C, (Db, C#), D, (Eb, D#), E, F

    # C4
    assert 261 == int(decode(res[0]["msg"])["args"]["freq"]), int(decode(res[0]["msg"])["args"]["freq"])

    # D#4 
    assert 311 == int(decode(res[3]["msg"])["args"]["freq"]), int(decode(res[3]["msg"])["args"]["freq"])

    ms2 = MetaSheet()
    ms2.sheet("hi4 5")
    samres = to_sequencer_sample_notes(ms2, "drum", "d1")
    message = decode(samres[0]["msg"])
    assert "hi" == message["family"]
    assert "freq" not in message["args"]
    assert "d1" == samres[0]["alias"]

