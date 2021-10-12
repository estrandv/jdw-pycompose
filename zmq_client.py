import zmq
import json

class PublisherClient:
    def __init__(self) -> None:
        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.PUSH)
        self.socket.connect("tcp://localhost:5559")
        #self.socket.recv()

    # Each note must contain {"target", "alias", "time", "args":{}}
    def queue(self, notes: list[dict]):
        #print(json.dumps([note["time"] for note in notes]))
        self.socket.send_string("JDW.SEQ.QUEUE::" + json.dumps(notes))

    def wipe(self, aliases: list[str]):
        payload = "JDW.SEQ.WIPE::" + json.dumps([{"alias": alias} for alias in aliases])
        print("wiping", payload)
        self.socket.send_string(payload)

    def nrt_record(self, notes: list[dict], bpm: int, filename: str, instrument_type: str):
        message = {"payload": notes, "bpm": bpm, "filename": filename, "type": instrument_type}
        self.socket.send_string("JDW.PROSC.NRT.RECORD::" + json.dumps(message))

    def update_synths(self):
        self.socket.send_string("JDW.PROSC.SYNDEF.UPDATE")

    def add_effect(self, events: list[dict]):
        #print(events)
        self.socket.send_string("JDW.ADD.EFFECT::" + json.dumps(events))

    def set_bpm(self, bpm: int):
        self.socket.send_string("JDW.SEQ.BPM::" + json.dumps(bpm))
        
    def wipe_effects(self):
        self.socket.send_string("JDW.REMOVE.EFFECTS")
        