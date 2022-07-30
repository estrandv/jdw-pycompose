# Package for new Message class (parsing.py) conversion into various jdw OSC formats 

from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
from pythonosc import udp_client
import new_parsing_july
import scales # TODO: This needs to come along
import time

def to_timed_osc(time: float, msg):
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    bundle.add_content(create_msg("/bundle_info", ["timed_msg"]))
    bundle.add_content(create_msg("/timed_msg_info", [time]))
    bundle.add_content(msg)
    return bundle.build()

def create_msg(adr: str, args = []):
    builder = osc_message_builder.OscMessageBuilder(address=adr)
    for arg in args:
        builder.add_arg(arg)
    return builder.build()

class MessageWrapper:
    def __init__(self, message: new_parsing_july.Message):
        self.message = message

    def to_sample_play(self):
        #time = self.message.args["sus"] if "sus" in self.message.args else 0.0
        # Silly default - not sure what a good other option is if tone is not mandatory 
        ext_id = self.message.suffix if self.message.suffix != "" else "sample" + ",".join(self.message.args)
        osc_args = []
        for key in self.message.args:
            osc_args.append(key)
            osc_args.append(self.message.args[key])
        return create_msg("/play_sample", [ext_id, "example", self.message.index, self.message.prefix] + osc_args)

    def to_note_on_timed(self, synth: str):

        # TODO: Hack for now - symbol resolution is better
        if synth == "sample":
            return self.to_sample_play()

        if "freq" not in self.message.args:
            self.message.create_freq_arg(scales.MAJOR, 2)

        time = self.message.args["sus"] if "sus" in self.message.args else 0.0
        # Silly default - not sure what a good other option is if tone is not mandatory 
        ext_id = self.message.suffix if self.message.suffix != "" else synth + ",".join(self.message.args)
        osc_args = []
        for key in self.message.args:
            osc_args.append(key)
            osc_args.append(self.message.args[key])
        return create_msg("/note_on_timed", [synth, ext_id, time] + osc_args)

    def get_time(self):
        return self.message.args["time"] if "time" in self.message.args else 0.0 
    
# TODO: Just gonna play with it here for now 

# "((0/(20/28)/22/(19/25))[attT0 >0.1 relT2 =0 #0.2 lfoS0.01 lfoD0.1] 1 3 (1 5)[=0.25] 2)[=0.5 #1.0 relT0.5 attT0.05 >0.1]"

# Hardcoded default port of jdw-sequencer main application


class OSCSender:
    def __init__(self):

        self.client = udp_client.SimpleUDPClient("127.0.0.1", 14441)

    def send(self, parse_string: str, synth = "gentle"):

        main_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        main_bundle.add_content(create_msg("/bundle_info", ["update_queue"]))
        main_bundle.add_content(create_msg("/update_queue_info", [synth + "_queue_id"]))

        bun = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

        messages = new_parsing_july.full_parse(parse_string)

        # TODO: Get rid of all the bug investigation from earlier - it's a server side issue
        for msg in messages:
            noti = MessageWrapper(msg)
            send_msg = noti.to_note_on_timed(synth)
            #wrp = to_timed_osc(noti.get_time(), create_msg("/s_new", []))

            wrp = to_timed_osc(noti.get_time(), send_msg)

            bun.add_content(wrp)

        main_bundle.add_content(bun.build())
        self.client.send(main_bundle.build())

sender = OSCSender()
sender.send("(bd0[=0 ofs0] (bd1/bd1/bd1/bd1) bd2[ofs0.2] ((bd1 bd2)[=0.5]/bd1) (sn0/to1)[=0 #0.5] bd2)[>1 =1 #1]", "sample")
sender.send("((0/(20/28)/22/(19/25))[attT0 >0.1 relT2 =0 #0.2 lfoS0.01 lfoD0.1] (1/1/1/1)[=0 #0] 1 3 (1 5)[=0.25] 2)[=0.5 #1.0 relT0.5 attT0.05 >0.1]")
# (0/(20/28)/22/(19/25))[attT0 >0.1 relT2 =0 #0.2 lfoS0.01 lfoD0.1] 