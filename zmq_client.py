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
