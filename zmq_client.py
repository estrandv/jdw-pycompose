import zmq
import json
import datetime
from parsing import parse_args

def timestamp_rfc3339():
    n = datetime.datetime.now(datetime.timezone.utc)
    return n.isoformat()

def msg(tag: str, timestamp: str, message: str):
    return tag + "::" + timestamp + "::" + message

class PublisherClient:
    def __init__(self) -> None:
        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.PUSH)
        self.socket.connect("tcp://localhost:5559")
        #self.socket.recv()

    # Each note must contain {"target", "alias", "time", "args":{}}
    def queue(self, notes: list[dict]):
        #print(json.dumps([note["time"] for note in notes]))
        self.socket.send_string(msg("JDW.SEQ.QUEUE", timestamp_rfc3339(), json.dumps(notes)))

    def wipe(self, aliases: list[str]):
        payload = msg("JDW.SEQ.WIPE", timestamp_rfc3339(), json.dumps([{"alias": alias} for alias in aliases]))
        print("wiping", payload)
        self.socket.send_string(payload)

    def nrt_record(self, notes: list[dict], bpm: int, filename: str, instrument_type: str):
        message = {"payload": notes, "bpm": bpm, "filename": filename, "type": instrument_type}
        self.socket.send_string(msg("JDW.PROSC.NRT.RECORD", timestamp_rfc3339(), json.dumps(message)))

    def update_synths(self):
        self.socket.send_string(msg("JDW.PROSC.SYNDEF.UPDATE", timestamp_rfc3339(), ""))

    def add_effect(self, events: list[dict]):
        self.socket.send_string(msg("JDW.ADD.EFFECT", timestamp_rfc3339(), json.dumps(events)))

    def set_effects(self, nested_list):
        contents = []
        for couple in nested_list:
            name = couple[0]
            arg_str = couple[1]
            args = parse_args(arg_str)
            contents_item = {
                "external_id": name + str(int(args["in"])) + "_pycompose", 
                "target": name, 
                "args": args
            }
            contents.append(contents_item)
        self.socket.send_string(msg("JDW.ADD.EFFECT", timestamp_rfc3339(), json.dumps(contents)))

    def set_bpm(self, bpm: int):
        self.socket.send_string(msg("JDW.SEQ.BPM", timestamp_rfc3339(), json.dumps(bpm)))
        
    def wipe_effects(self):
        self.socket.send_string(msg("JDW.REMOVE.EFFECTS", timestamp_rfc3339(), ""))
        