# Run everything that should happen only once 

import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils
from pythonosc import udp_client 
from pythonosc.osc_packet import OscPacket
import sample_reading
import default_synthdefs
import time

# TODO: make something smarter later - for now just run it directly... 
client = udp_client.SimpleUDPClient("127.0.0.1", 13339) # Router

def get_oneshot_messages() -> list[OscPacket]:
    return [
        jdw_osc_utils.create_msg("/note_on", ["reverb", "reverb_effect_2", 0, "inBus", 4.0, "outBus", 0.0])
    ]

if __name__ == "__main__":

    # BPM set example
    #client.send(create_msg("/set_bpm", [tracks.bpm]))

    for sample in sample_reading.read_sample_packs("~/sample_packs"):
        client.send(jdw_osc_utils.create_msg("/load_sample", sample.as_args()))

    for synthdef in default_synthdefs.get():
        client.send(jdw_osc_utils.create_msg("/create_synthdef", [synthdef]))

    time.sleep(0.2)

    for oneshot in get_oneshot_messages():
        client.send(oneshot)