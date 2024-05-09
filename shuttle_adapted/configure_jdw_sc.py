# Run everything that should happen only once 

import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils
from pythonosc import udp_client 
from pythonosc.osc_packet import OscPacket
import sample_reading
import default_synthdefs
import time

# TODO: make something smarter later - for now just run it directly... 
client = udp_client.SimpleUDPClient("127.0.0.1", 13339) # Router

# Messages that should only fire when this particular script is run (once per server boot), but also
#   be available for NRT record messages 
def get_oneshot_messages() -> list[OscPacket]:
    return [
        # Note that effects, control tracks and drones all work well in this category
        # Note also that a drone can be launched with amp0 and then modified during sequence tracks as needed 
        jdw_osc_utils.create_msg("/note_on", ["reverb", "reverb_effect_1", 0, "inBus", 4.0, "outBus", 0.0]),
        jdw_osc_utils.create_msg("/note_on", ["control", "cs", 0, "bus", 55.0, "prt", 0.5])
    ]

if __name__ == "__main__":

    # BPM set example
    #client.send(create_msg("/set_bpm", [tracks.bpm]))

    for sample in sample_reading.read_sample_packs("~/sample_packs"):
        client.send(jdw_osc_utils.create_msg("/load_sample", sample.as_args()))

    for synthdef in default_synthdefs.get():
        client.send(jdw_osc_utils.create_msg("/create_synthdef", [synthdef]))

    time.sleep(0.5)

    for oneshot in get_oneshot_messages():
        client.send(oneshot)