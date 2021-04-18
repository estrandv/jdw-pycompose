import zmq
import json


class PublisherClient:
    def __init__(self) -> None:
        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5559")

    # Each note must contain {"target", "alias", "time", "args":{}}
    def queue_synth(self, notes: list[dict]):
        self.socket.send_string("JDW.SEQ.QUE.NOTES::" + json.dumps(notes))
        self.socket.recv()

    def queue_sample(self, notes: list[dict]):
        self.socket.send_string("JDW.SEQ.QUE.SAMPLES::" + json.dumps(notes))
        self.socket.recv()
