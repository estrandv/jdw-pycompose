import zmq
import json

class PublisherClient:
    def __init__(self) -> None:
        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5559")

    # Each note must contain {"target", "alias", "time", "args":{}}
    def queue(self, notes: list[dict]):
        self.socket.send_string("JDW.SEQ.QUEUE::" + json.dumps(notes))
        self.socket.recv()

    def update_synths(self):
        self.socket.send_string("JDW.PROSC.SYNDEF.UPDATE")
        self.socket.recv()

    def add_effect(self, events: list[dict]):
        self.socket.send_string("JDW.ADD.EFFECT::" + json.dumps(events))
        self.socket.recv()

    def set_bpm(self, bpm: int):
        self.socket.send_string("JDW.SEQ.BPM::" + json.dumps(bpm))
        self.socket.recv()