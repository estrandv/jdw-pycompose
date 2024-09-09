# Purpose: Highest-level billboarding calls for the main usage scenarios (setup/configure/run/nrt).

from time import sleep
from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_message import OscMessage
from pythonosc.udp_client import SimpleUDPClient
from billboard_osc_conversion import NrtBundleInfo, get_all_command_messages, get_all_effects_create, get_all_effects_mod, get_nrt_record_bundles, get_sampler_keyboard_config, get_sequencer_batch_queue_bundle, get_synth_keyboard_config
from billboarding import parse_billboard

from billboarding import Billboard
from default_configuration import get_default_samples, get_default_synthdefs, get_effects_clear
from parsing import CommandContext
from jdw_osc_utils import create_nrt_preload_bundle
import default_synthdefs as default_synthdefs
import sample_reading as sample_reading

def default_client() -> SimpleUDPClient:
    return SimpleUDPClient("127.0.0.1", 13339) # Router

# One-time stups like loading all default synths (many messages, time-intensive)
def setup(bdd_path: str):
    client = default_client()

    with open(bdd_path, 'r') as bdd_file:
        billboard: Billboard = parse_billboard(bdd_file.read())

        all_messages: list[OscMessage] = [sample.load_msg for sample in get_default_samples()] + [synth.load_msg for synth in get_default_synthdefs()]

        for msg in all_messages:
            sleep(0.005) # Seems to be needed to prevent dropped messages. This is a tested minimum for 100% configure.
            client.send(msg)

def configure(bdd_path: str):
    client = default_client()


    with open(bdd_path, 'r') as bdd_file:
        billboard: Billboard = parse_billboard(bdd_file.read())

        all_messages: list[OscMessage] = []

        all_messages += get_sampler_keyboard_config(billboard)
        all_messages += get_synth_keyboard_config(billboard)

        all_messages += [get_effects_clear()]
        all_messages += get_all_command_messages(billboard, [CommandContext.ALL, CommandContext.UPDATE])
        all_messages += get_all_effects_create(billboard)

        for msg in all_messages:
            sleep(0.005) # Seems to be needed to prevent dropped messages. This is a tested minimum for 100% configure.
            client.send(msg)

def nrt_record(bdd_path: str):
    client = default_client()
    with open(bdd_path, 'r') as bdd_file:

        billboard: Billboard = parse_billboard(bdd_file.read())
        bundle_infos: list[NrtBundleInfo] = get_nrt_record_bundles(billboard)
        for info in bundle_infos:
            print("DEBUG: NRT recording", info.track_name)
            for preload in info.preload_messages:
                # TODO: We can batch this too, ya know
                client.send(preload)
                sleep(0.005) # Arbitrary "that should do it" wait time to avoid dropping packets

            # Just some batching hack I stole off stackoverflow
            batch_size = 10
            preload_batches = [info.preload_bundles[i * batch_size:(i + 1) * batch_size] for i in range((len(info.preload_bundles) + batch_size - 1) // batch_size )]
            for batch in preload_batches:
                client.send(create_nrt_preload_bundle(batch))
                sleep(0.005)

            client.send(info.nrt_bundle)


def update_queue(bdd_path: str):
    client = default_client()

    with open(bdd_path, 'r') as bdd_file:
        billboard: Billboard = parse_billboard(bdd_file.read())

        all_messages: list[OscMessage | OscBundle] = []

        # Keyboard is configured on regular run as well
        all_messages += get_synth_keyboard_config(billboard)
        all_messages += get_sampler_keyboard_config(billboard)
        all_messages += get_all_command_messages(billboard, [CommandContext.ALL, CommandContext.QUEUE])
        all_messages += get_all_effects_mod(billboard)
        all_messages += [get_sequencer_batch_queue_bundle(billboard)]

        for msg in all_messages:
            sleep(0.005) # Seems to be needed to prevent dropped messages
            client.send(msg)
