# Package for new Message class (parsing.py) conversion into various jdw OSC formats 

from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
import parsing
import scales
import time
from enum import Enum

# Debugging 
import json 

# jdw_sc needs a delay for even sequencing
# This is mainly for usage with jdw-sequencer and isn't relevant for direct input
# Should ideally be dynamic I guess
SC_DELAY_MS = 70

class SendType(Enum):
    NOTE_ON_TIMED = 0
    PLAY_SAMPLE = 1
    NOTE_MOD = 2
    NOTE_ON = 3
    EMPTY = 4


# Wrap a parsig.Message in an execution time - used by generic message transform after parsing 
def to_timed_osc(time: float, osc_packet):
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    bundle.add_content(create_msg("/bundle_info", ["timed_msg"]))
    bundle.add_content(create_msg("/timed_msg_info", [time]))
    bundle.add_content(osc_packet)
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
        return create_msg("/play_sample", [ext_id, sample_pack_name, self.message.index, self.message.prefix, SC_DELAY_MS] + osc_args)

    def to_note_modify(self, scale=scales.MINOR, octave=3):
        if "freq" not in self.message.args:
            self.message.create_freq_arg(scale, octave)

        # Silly external note id default - not sure what a good other option is if tone is not mandatory 
        ext_id = self.message.suffix if self.message.suffix != "" else "random_nset_id"
        osc_args = []
        for key in self.message.args:
            osc_args.append(key)
            osc_args.append(self.message.args[key])
        return create_msg("/note_modify", [ext_id, SC_DELAY_MS] + osc_args)

    def to_note_on_timed(self, synth: str):

        if "freq" not in self.message.args:
            # TODO: Kinda stupid, hidden inferrence that is just here for convenience.
            # Idea is that we do letter parsing if the prefix matches a note letter, otherwise we go index notes with provided octave 
            # TODO: Also note that this has no testing and currently does not apply to note mod or note on drones 
            letter_check = parsing.note_letter_to_midi(self.message.prefix)
            if letter_check == -1:
                self.message.create_freq_arg(scales.MAJOR, 3)
            else:
                self.message.create_letter_freq_arg()

        time = str(self.message.args["gate_time"]) if "gate_time" in self.message.args else "0.0"
        # Silly external note id default - not sure what a good other option is if tone is not mandatory 
        ext_id = self.message.suffix if self.message.suffix != "" else synth + ",".join(self.message.args)
        osc_args = []
        for key in self.message.args:
            osc_args.append(key)
            osc_args.append(self.message.args[key])
        return create_msg("/note_on_timed", [synth, ext_id, time, SC_DELAY_MS] + osc_args)

    def to_note_on(self, synth: str):
        if "freq" not in self.message.args:
            self.message.create_freq_arg(scales.MINOR, 3)

        # Silly default - not sure what a good other option is if tone is not mandatory 
        ext_id = self.message.suffix if self.message.suffix != "" else synth + ",".join(self.message.args)
        osc_args = []
        for key in self.message.args:
            osc_args.append(key)
            osc_args.append(self.message.args[key])
        return create_msg("/note_on", [synth, ext_id, SC_DELAY_MS] + osc_args)

    def get_time(self):
        return str(self.message.args["time"]) if "time" in self.message.args else "0.0" 


