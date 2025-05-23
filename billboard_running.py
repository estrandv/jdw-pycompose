# Purpose: Highest-level billboarding calls for the main usage scenarios (setup/configure/run/nrt).

from time import sleep
from jdw_billboarding.lib.external_data_classes import SampleMessage, SynthDefMessage
from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_message import OscMessage
from pythonosc.udp_client import SimpleUDPClient
from jdw_billboarding.lib import jdw_osc_utils


from file_utilities import get_default_samples, get_default_synthdefs

from jdw_billboarding import get_configuration_messages, NrtData, get_nrt_data, get_queue_update_packets, get_silence_drones

from listener import Listener

import macros
import re
import os

def resolve_macros(file_path: str) -> str:
    content = open(file_path, 'r').read()
    common_content = open(os.path.dirname(file_path) + "/common_macros.txt", 'r').read()
    #print("COMMON CONTENT", common_content)
    common_defs = macros.find_macro_defs(common_content)
    print("DEFS", common_defs)
    common_macros = [macros.parse_macro_def(d) for d in common_defs]
    print("COMMON", common_macros)
    return macros.compile_macros(content, common_defs)

def default_client() -> SimpleUDPClient:
    return SimpleUDPClient("127.0.0.1", 13339) # Router

# One-time stups like loading all default synths (many messages, time-intensive)
# TODO: Get things from file_utilities and also provide them to nrt_record
def setup(_bdd_path: str):
    client = default_client()

    all_messages: list[OscMessage] = [sample.load_msg for sample in get_default_samples()] + [synth.load_msg for synth in get_default_synthdefs()]

    for msg in all_messages:
        sleep(0.005) # Seems to be needed to prevent dropped messages. This is a tested minimum for 100% configure.
        client.send(msg)

def quiet(bdd_path: str):
    default_client().send(jdw_osc_utils.create_msg("/hard_stop", []))
    # Note that this kills any existing drones with freeSelf, which will have to be manually recreated
    default_client().send_message("/note_modify", [
        "^(?!effect_).*$",
        0,
        "gate",
        0.0
    ])
    bdd_file = resolve_macros(bdd_path)
    for m in get_silence_drones(bdd_file):
        sleep(0.005)
        default_client().send(m)


    #beep()
    # TODO: Modify above modify to ignore effects and drones and only target notes
    # TODO: Include all_drones_silence call here

def configure(bdd_path: str):
    client = default_client()

    bdd_file = resolve_macros(bdd_path)
    all_messages: list[OscMessage] = get_configuration_messages(bdd_file)
    all_messages += [synth.load_msg for synth in get_default_synthdefs()] # TODO: Including synths for easy prototyping
    for msg in all_messages:
        sleep(0.001) # Not 100% sure this is needed anymore but it's nice when configure doesn't drop any packets'
        client.send(msg)

def nrt_record(bdd_path: str):
    client = default_client()

    print("LISTENER LIVE")

    synthdefs: list[SynthDefMessage] = get_default_synthdefs()
    samples: list[SampleMessage] = get_default_samples()
    lis = Listener()

    bdd_file = resolve_macros(bdd_path)

    nrt_data: list[NrtData] = get_nrt_data(bdd_file, synthdefs, samples)

    for nrt_track in nrt_data:
        for preload in nrt_track.preload_messages:
            # TODO: We can batch this too, ya know
            client.send(preload)
            sleep(0.005) # Arbitrary "that should do it" wait time to avoid dropping packets
        for batch in nrt_track.preload_bundle_batches:
            client.send(batch)
            sleep(0.005)
        client.send(nrt_track.main_bundle)
        lis.wait_for("/nrt_record_finished")

def update_queue(bdd_path: str):
    client = default_client()

    bdd_file = resolve_macros(bdd_path)

    packets: list[OscMessage | OscBundle] = get_queue_update_packets(bdd_file)
    for p in packets:
        sleep(0.005) # Seems to be needed to prevent dropped messages
        client.send(p)
