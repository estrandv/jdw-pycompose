# Purpose: Highest-level billboarding calls for the main usage scenarios (setup/configure/run/nrt).

from time import sleep
from jdw_billboarding.lib.external_data_classes import SampleMessage, SynthDefMessage
from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_message import OscMessage
from pythonosc.udp_client import SimpleUDPClient

from file_utilities import get_default_samples, get_default_synthdefs

from jdw_billboarding import get_configuration_messages, NrtData, get_nrt_data, get_queue_update_packets

from listener import Listener

import macros
import re

def resolve_macros(file_path: str) -> str:
    content = open(file_path, 'r').read()

    macro_part_pre = re.search("(?<=<macros>)[\\s\\S]*?(?=</macros>)", content)

    macro_part = macro_part_pre.group() if macro_part_pre else ""

    non_macro_part = content.split("</macros>")[1] if "</macros>" in content else content

    return macros.compile_macros(macro_part, non_macro_part)

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
