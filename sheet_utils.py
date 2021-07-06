from typing import Iterable
from copy import deepcopy
import json

class PostingType:
    def __init__(self, id: int):
        self.id = id

class PostingTypes:
    PROSC = PostingType(0)
    SAMPLE = PostingType(1)
    MIDI = PostingType(2)

# Mostly because I'm too lazy to rename across the board ... 
def _streamline(note: dict[str, float]):
    exported = {}
    for key in note:

        # TODO: Dirty hack until harmonized
        if key == "tone":
            exported["freq"] = note[key]
        elif key == "reserved_time": # TODO: Also clumsy 
            exported["time"] = note[key]            
        else:
            exported[key] = note[key]

    return exported

def export_nrt(note: dict[str, float], target: str):
    exported = {"target": target, "args": {}}

    for key in _streamline(note):
        exported["args"][key] = _streamline(note)[key]

    return exported 
        

# Transform the local note dict into the api expected format 
# TODO: Bit of a mess, but the end goal is to transform notes into the zeromq sequencer format
def _export_note(note: dict[str, float], synth_name: str, sequencer_id: str, posting_type: PostingType):
    # {alias, time, "msg: XXX::{target, args}"}
    sequencer_message: dict[str, Any] = {"alias": sequencer_id}
    exported = {"target": synth_name, "args": {}}

    amp = note["amp"] if "amp" in note else 0.0

    # Should throw error if missing; mandatory 
    sequencer_message["time"] = note["reserved_time"]

    for key in _streamline(note):
        exported["args"][key] = _streamline(note)[key]

    payload = json.dumps(exported)

    # Don't order sequencer to actually play any "silent" notes
    if amp == 0.0:
        payload = "{}"

    if posting_type == PostingTypes.PROSC:
        sequencer_message["msg"] = "JDW.PLAY.NOTE::" + payload
    elif posting_type == PostingTypes.SAMPLE:
        sequencer_message["msg"] = "JDW.PLAY.SAMPLE::" + payload
    elif posting_type == PostingTypes.MIDI:
        # TODO: sus Ms in actual sus ms 
        midi_msg = {"target": exported["target"],"tone": exported["args"]["freq"], "sus_ms": exported["args"]["sus"], "amp": exported["args"]["amp"]}
        midi_payload = json.dumps(midi_msg)

        # TODO: Dont play on 0 amp 

        sequencer_message["msg"] = "JDW.PLAY.MIDI::" + midi_payload

    return sequencer_message


# Transform any set of integer lists into the sheet-standard of "0 0 0 . 1 0 1" etc. 
# Each list is another chunk separated by a dot, the above would be the same as: [0,0,0], [1,0,1]
# Useful if you want to utilize python list generators such as range()
def arr_fmt(*lists: Iterable[int]) -> str:
    return " . ".join([" ".join(slst) for slst in [[str(i) for i in lst] for lst in lists]])

def _merge_note(under: dict[str, float], over: dict[str, float]) -> dict[str, float]:
    
    merged = deepcopy(under)

    for attr in over:
        merged[attr] = over[attr]

    return merged