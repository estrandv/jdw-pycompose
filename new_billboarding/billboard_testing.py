# WIP all-in-one calls to JDW via new billboard


from time import sleep
from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_message import OscMessage
from pythonosc.udp_client import SimpleUDPClient
from billboard_osc_conversion import NrtBundleInfo, get_all_command_messages, get_all_effects_create, get_all_effects_mod, get_nrt_record_bundles, get_sampler_keyboard_config, get_sequencer_batch_queue_bundle, get_synth_keyboard_config
from billboarding import parse_billboard

from billboarding import Billboard
from default_configuration import get_default_samples, get_default_synthdefs, get_effects_clear
from billboarding import CommandContext
import temp_import.default_synthdefs as default_synthdefs
import temp_import.sample_reading as sample_reading

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

        """

            Most filtering now works, but there are some remaining issues:
                - Even with heavy filtering, tracks with many notes are still too big and we will have to move towards a preload approach to scoring
                    - This does not have to break the current structure at all, but will take some implementation in jdw-sc
                - I reworked samples to no longer loop-around modulo and instead require exact indices... see if this had any effect on the keyboards

        """

        billboard: Billboard = parse_billboard(bdd_file.read())
        bundle_infos: list[NrtBundleInfo] = get_nrt_record_bundles(billboard)
        for info in bundle_infos:
            # TODO: Testing if any tracks are short enough for single-send
            #if info.track_name == "Roland808_drum_0":
            #if info.track_name not in ["Roland808_drum_0", "Roland808_hdrum_2"]:
            if True:
                print("DEBUG: NRT recording", info.track_name)
                for preload in info.preload_messages:
                    client.send(preload)
                    sleep(0.005)
                client.send(info.nrt_bundle)
            #else:
            #    print("DEBUG: NOT RIGHT", info.track_name)


def update_queue(bdd_path: str):
    client = default_client()

    with open(bdd_path, 'r') as bdd_file:
        billboard: Billboard = parse_billboard(bdd_file.read())

        all_messages: list[OscMessage | OscBundle] = []

        # Keyboard is configured on regular run as well
        all_messages += get_synth_keyboard_config(billboard)
        all_messages += get_sampler_keyboard_config(billboard)

        # TODO: effects mod seems to behave a bit weirdly - might be because new method fails to give them unique ids if they dont have a group
        #   - UPDATE: Yes. I think regex might actually grab "effect_a_" as a match for all with e.g. "effect_a_mygroup". This is a bit unintuitive but not really a bug...
        # TODO: Split default synths by ";" instead and just make it an scd file for proper highlighting
        # TODO: Default synths and sample config should both be neat files like the bbd to allow them to live in another repo
        # TODO: In the future, we might want to be able to specify sample loading in bbd
        all_messages += get_all_command_messages(billboard, [CommandContext.ALL, CommandContext.QUEUE])
        all_messages += get_all_effects_mod(billboard)
        all_messages += [get_sequencer_batch_queue_bundle(billboard)]

        for msg in all_messages:
            sleep(0.005) # Seems to be needed to prevent dropped messages
            client.send(msg)

example = "/home/estrandv/programming/jdw-pycompose/songs/courtRide.bbd"
#setup(example)
#configure(example)
#update_queue(example)
nrt_record(example)
