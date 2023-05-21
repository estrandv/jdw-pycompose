# Package for new Message class (parsing.py) conversion into various jdw OSC formats 

from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
from pythonosc import udp_client
import parsing
import scales
import time
import uuid
from enum import Enum


# Debugging 
import json 

class SendType(Enum):
    NOTE_ON_TIMED = 0
    PLAY_SAMPLE = 1
    NOTE_MOD = 2
    NOTE_ON = 3
    EMPTY = 4


# Wrap a parsig.Message in an execution time - used by generic message transform after parsing 
def to_timed_osc(time: float, msg: parsing.Message):
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    bundle.add_content(create_msg("/bundle_info", ["timed_msg"]))
    bundle.add_content(create_msg("/timed_msg_info", [time]))
    bundle.add_content(msg)
    return bundle.build()

# Basic quick-syntax for OSC message building, ("/s_new, [1,2,3...]")
def create_msg(adr: str, args = []):
    builder = osc_message_builder.OscMessageBuilder(address=adr)
    for arg in args:
        builder.add_arg(arg)
    return builder.build()

class MessageWrapper:
    def __init__(self, message: parsing.Message):
        self.message = message

    def get_type(self) -> SendType:
        if self.message.symbol == ":":
            return SendType.NOTE_MOD
        elif self.message.symbol == "_":
            return SendType.EMPTY
        elif self.message.symbol == "$":
            return SendType.NOTE_ON
        return None

    # Internally resolve the right conversion method by detecting type from symbol/default
    def to_osc(self, default_type: SendType, synth):
        type = self.get_type()
        type = type if type != None else default_type

        send_msg = []
        if type == SendType.PLAY_SAMPLE:
            send_msg = self.to_sample_play(synth)
        elif type == SendType.NOTE_MOD:
            # n_set
            send_msg = self.to_note_modify()
        elif type == SendType.EMPTY:
            # Timing still works - see to_timed_msg call below 
            send_msg = create_msg("/empty_msg")
        elif type == SendType.NOTE_ON:
            send_msg = self.to_note_on(synth)
        elif type == SendType.NOTE_ON_TIMED:
            send_msg = self.to_note_on_timed(synth)

        return send_msg

    def to_sample_play(self, sample_pack_name):

        # Silly external note id default - not sure what a good other option is if tone is not mandatory 
        ext_id = self.message.suffix if self.message.suffix != "" else "sample" + ",".join(self.message.args)
        
        osc_args = []
        for key in self.message.args:
            osc_args.append(key)
            osc_args.append(self.message.args[key])
        return create_msg("/play_sample", [ext_id, sample_pack_name, self.message.index, self.message.prefix] + osc_args)

    def to_note_modify(self, scale=scales.MINOR, octave=3):
        if "freq" not in self.message.args:
            self.message.create_freq_arg(scale, octave)

        # Silly external note id default - not sure what a good other option is if tone is not mandatory 
        ext_id = self.message.suffix if self.message.suffix != "" else "random_nset_id"
        osc_args = []
        for key in self.message.args:
            osc_args.append(key)
            osc_args.append(self.message.args[key])
        return create_msg("/note_modify", [ext_id] + osc_args)

    def to_note_on_timed(self, synth: str):

        if "freq" not in self.message.args:
            self.message.create_freq_arg(scales.MAJOR, 3)

        time = self.message.args["gate_time"] if "gate_time" in self.message.args else 0.0
        # Silly external note id default - not sure what a good other option is if tone is not mandatory 
        ext_id = self.message.suffix if self.message.suffix != "" else synth + ",".join(self.message.args)
        osc_args = []
        for key in self.message.args:
            osc_args.append(key)
            osc_args.append(self.message.args[key])
        return create_msg("/note_on_timed", [synth, ext_id, time] + osc_args)

    def to_note_on(self, synth: str):
        if "freq" not in self.message.args:
            self.message.create_freq_arg(scales.MINOR, 3)

        # Silly default - not sure what a good other option is if tone is not mandatory 
        ext_id = self.message.suffix if self.message.suffix != "" else synth + ",".join(self.message.args)
        osc_args = []
        for key in self.message.args:
            osc_args.append(key)
            osc_args.append(self.message.args[key])
        return create_msg("/note_on", [synth, ext_id] + osc_args)

    def get_time(self):
        return self.message.args["time"] if "time" in self.message.args else 0.0 
    
client = udp_client.SimpleUDPClient("127.0.0.1", 13339) # Router
client.send(create_msg("/set_bpm", [120]))


# TODO: Sketch up of the above outline
class Synth():
    def __init__(self, parse: str, ext_id = ""):

        # TODO: Most of tis copy pasted from (replacing) sender.send() 

        # TODO: Could also be a builder method with this as default 
        if ext_id == "": 
            ext_id = "autogen_queue_id_" + str(uuid.uuid4())

        self.ext_id = ext_id

        messages = parsing.full_parse(parse)

        self.msg_wrappers = []
        for msg in messages: 
            msg.add_missing_args({"time": 1.0, "gate_time": 0.1, "amp": 1.0})
            self.msg_wrappers.append(MessageWrapper(msg))

    def nrt_record(self, synth: str, default_type = SendType.NOTE_ON_TIMED):
        main_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

        bun = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        
        timeline = 0
        for wrapper in self.msg_wrappers:

            send_msg = wrapper.to_osc(default_type, synth)

            # TODO: With wrapper resolving the above internally, you can also do this baking 
            print("DEBUG: resolved time on message: ", str(wrapper.get_time()))
            wrp = to_timed_osc(wrapper.get_time(), send_msg)
            bun.add_content(wrp)
            timeline += wrapper.get_time()


        main_bundle.add_content(create_msg("/bundle_info", ["nrt_record"]))
        main_bundle.add_content(create_msg("/nrt_record_info", [120.0, self.ext_id + ".wav", timeline]))
        main_bundle.add_content(bun.build())

        # TODO: Global client 
        client.send(main_bundle.build())


    # TODO: play/play_sample might be simpler than default type
    # But you can easily make those call this 
    def play(self, synth: str, default_type = SendType.NOTE_ON_TIMED):

        main_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        main_bundle.add_content(create_msg("/bundle_info", ["update_queue"]))
        # NOTE: Meta-info for the update-queue command, mainly the external id of the sequencer 
        main_bundle.add_content(create_msg("/update_queue_info", [self.ext_id]))

        bun = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        for wrapper in self.msg_wrappers:

            send_msg = wrapper.to_osc(default_type, synth)


            # TODO: With wrapper resolving the above internally, you can also do this baking 
            print("DEBUG: resolved time on message: ", str(wrapper.get_time()))
            wrp = to_timed_osc(wrapper.get_time(), send_msg)
            bun.add_content(wrp)
        main_bundle.add_content(bun.build())

        # TODO: Global client 
        client.send(main_bundle.build())

