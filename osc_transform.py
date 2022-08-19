# Package for new Message class (parsing.py) conversion into various jdw OSC formats 

from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
from pythonosc import udp_client
import new_parsing_july
import scales # TODO: This needs to come along
import time
import uuid

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
        return create_msg("/play_sample", [ext_id, "KB6", self.message.index, self.message.prefix] + osc_args)

    def to_note_modify(self, scale=scales.MINOR, octave=3):
        if "freq" not in self.message.args:
            self.message.create_freq_arg(scale, octave)

        # Silly default - not sure what a good other option is if tone is not mandatory 
        ext_id = self.message.suffix if self.message.suffix != "" else "random_nset_id"
        osc_args = []
        for key in self.message.args:
            osc_args.append(key)
            osc_args.append(self.message.args[key])
        return create_msg("/note_modify", [ext_id] + osc_args)

    def to_note_on_timed(self, synth: str):

        if "freq" not in self.message.args:
            self.message.create_freq_arg(scales.MINOR, 3)

        time = self.message.args["gate_time"] if "gate_time" in self.message.args else 0.0
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


class OSCSender:
    def __init__(self):
        # Hardcoded default port of jdw-sequencer main application

        #self.client = udp_client.SimpleUDPClient("127.0.0.1", 14441)
        self.client = udp_client.SimpleUDPClient("127.0.0.1", 13339) # Router 

    def send(self, parse_string: str, synth = "gentle", ext_id = None):

        # TODO: HIdden defaults for convenience
        parse_string = "(" + parse_string + ")[=1 >1 #1]"

        if ext_id == None: 
            ext_id = "autogen_queue_id_" + str(uuid.uuid4())

        main_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        main_bundle.add_content(create_msg("/bundle_info", ["update_queue"]))
        main_bundle.add_content(create_msg("/update_queue_info", [ext_id]))

        bun = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

        messages = new_parsing_july.full_parse(parse_string)

        # TODO: Get rid of all the bug investigation from earlier - it's a server side issue
        for msg in messages:
            noti = MessageWrapper(msg)

            # TODO: Expand symbol interpretation here 
            send_msg = []
            if synth == "sample":
                # TODO: It ain't a beauty but it works 
                send_msg = noti.to_sample_play()
            elif noti.message.symbol == ":":
                send_msg = noti.to_note_modify()
            else:
                send_msg = noti.to_note_on_timed(synth)

            wrp = to_timed_osc(noti.get_time(), send_msg)

            bun.add_content(wrp)

        main_bundle.add_content(bun.build())
        self.client.send(main_bundle.build())

    def send_raw(self, packet):
        self.client.send(packet)

sender = OSCSender()
#sender.send("(1 2 3 4)[>0.5 =1 #1 relT0.2]")
sender.send_raw(create_msg("/set_bpm", [120]))
# TODO: Seems to get a bit wonky in certain sus settings
# TODO: Trying to figure out the "lazy drummer feel"
# On seemingly random notes there is sometimes a sort of "eeeeehBAM" catching-up feeling 
# I don't think it's related to sequence reset because I've tried longer sequences and it's present mid-play
# I don't think it's messaging since UDP should be fast enough and the problem doesn't seem to worsen
#   when playing multiple (but this could be explored more)
# One lead is the strange behaviour with SUS for sampler and whether n_set over s_new has an impact 
#   - But n_set is a philosophical issue for a synth that only plays once on start 
#sender.send("(bd0 (bd0/bd0/bd0/bd0) (bd0 bd0)[=0.5] bd0)[=1 #1 relT0.2 >0.4 ofs0]", "sample")

# TODO: Example for non-number note resolution (comfortably octave 3 as default) 
example_note_string = "(g e+4 (c4 c)[=0.5] d)[=1 >1 #1]"

# Cute 
#sender.send("(bd1 sn1 (bd1 bd2)[=0.5] sn1)[=1 >1 #3 ofs0.04]", "sample", "drum1")
#sender.send("((1/3/1/6)[=0] 2 2 (3/(4/5))[relT0.4] 2)[=0.5 >0.25 #0.2 relT0.2]", "gentle", "slim")
#sender.send("(8 9 (7/2) 5)[=4 >1 #0.2 relT0.8]", "gentle", "slim2")

# Drone test 
#sender.send("(2 5 9)[>0.02 =0.5 #1 lfoS0.28 susL0.1 decT0.25 lfoD0.24 relT2.5 attT0.05 fx0.23]", "brute", "dron1")

# TODO: Neat features I think about while coding
# 1. "1/8" division syntax for args so that we dont have to figure out what "3/8" is in decimal
# 2. "simplify()" call or similar to "hold off" parenthesis parsing; "as if index 0" or something. Good for live. 
# 3. Wipe feature so that non-mentioned are removed. Could be tricky. 

# Cute - note that this used sample pack "example" 
#sender.send("((bd2/(bd2[=0.5] bd2[=1.5])) (bd1[ofs0.18]/sn0[ofs0.24 #2.4]))[ofs0.1 relT2 >10 =2]", "sample", "drum_one")
#sender.send("((10/8/7/8)[=0 relT4 #0.3 >2 lfoS0.01 lfoD0.2] 1 ((2/6)/8) 4 (3/(4 4)[=0.5 >0.1]))[relT0.1]", "gentle", "gentle_one")
#sender.send("(sh1[ofs0.2] to0[ofs1.2] sn0 bd2)[=0.5 #0.1]", "sample", "tics")
#sender.send("(9 (9/14[relT0.4 >0.3]) 9 ((7/11)/4) 8 (6/15[lfoS0.02 lfoD0.4 relT1]) 5 7)[#0.08 >0.1 relT0.25 =0.5]", "brute", "brutalize")

sender.send("((0 12)[=0.5] (1/(9 12)[=0.5]) ((2 3)[=0.5]/7[ofs0]) 4)[ofs0.06]", "sample", "sample_pl")
sender.send("((2/(3 6)[=0.5]) (3[pan0.3]/3[pan-0.3]) (4/11)[wid2 #0.2 >0.5] (5/(8/12)))[>0.1 sus1 dec0 att0.25 rel0.8 wid0.8]", "varsaw", "var_saw")