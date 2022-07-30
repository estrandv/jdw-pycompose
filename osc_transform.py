# Package for new Message class (parsing.py) conversion into various jdw OSC formats 

from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
from pythonosc import udp_client
import new_parsing_july
import scales # TODO: This needs to come along

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

    def to_note_on_timed(self, synth: str):

        if "freq" not in self.message.args:
            self.message.create_freq_arg(scales.MAJOR, 3)

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

# Hardcoded default port of jdw-sequencer main application
client = udp_client.SimpleUDPClient("127.0.0.1", 14441)

main_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
main_bundle.add_content(create_msg("/bundle_info", ["update_queue"]))
main_bundle.add_content(create_msg("/update_queue_info", ["python_test_queue"]))

bun = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
# TODO: Somehow there is a get_bundle(1) error for the full queue message if we have too many
# notes in the parse..? 
# UPDATE: Might actually be something with the length of the parse....? 
for msg in new_parsing_july.full_parse("(0[>4 lfoS22.2 lfoD0.2] (9/8)[fx3.0 >1.0 #0.5] 4)[=1.0 #1.0 relT0.0 attT0.05 >0.1]"):
    noti = MessageWrapper(msg)
    time = noti.get_time()
    wrp = to_timed_osc(noti.get_time(), noti.to_note_on_timed("brute"))
    print("Msg info ", msg.__dict__)

    bun.add_content(wrp)

main_bundle.add_content(bun.build())

client.send(main_bundle.build())