# WIP all-in-one calls to JDW via new billboard


from time import sleep
from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_message import OscMessage
from pythonosc.udp_client import SimpleUDPClient
from billboard_osc_conversion import get_all_command_messages, get_all_effects_create, get_all_effects_mod, get_sampler_keyboard_config, get_sequencer_batch_queue_bundle, get_synth_keyboard_config
from billboarding import parse_billboard

from billboarding import Billboard
from default_configuration import get_default_samples, get_default_synthdefs, get_effects_clear
import temp_import.default_synthdefs as default_synthdefs
import temp_import.sample_reading as sample_reading

def configure(bdd_path: str):
    client = SimpleUDPClient("127.0.0.1", 13339) # Router, should normally just use default

    with open(bdd_path, 'r') as bdd_file:
        billboard: Billboard = parse_billboard(bdd_file.read())

        all_messages: list[OscMessage] = []


        # Note that this loads -a lot- of stuff and should maybe be placed in a separate "boot config" run
        #all_messages += [sample.load_msg for sample in get_default_samples()]
        #all_messages += [synth.load_msg for synth in get_default_synthdefs()]


        all_messages += get_sampler_keyboard_config(billboard)
        all_messages += get_synth_keyboard_config(billboard)

        all_messages += [get_effects_clear()]
        all_messages += get_all_command_messages(billboard)
        all_messages += get_all_effects_create(billboard)

        for msg in all_messages:
            sleep(0.005) # Seems to be needed to prevent dropped messages. This is a tested minimum for 100% configure.
            client.send(msg)

def update_queue(bdd_path: str):
    client = SimpleUDPClient("127.0.0.1", 13339) # Router, should normally just use default


    with open(bdd_path, 'r') as bdd_file:
        billboard: Billboard = parse_billboard(bdd_file.read())

        all_messages: list[OscMessage | OscBundle] = []

        # Keyboard is configured on regular run as well
        all_messages += get_synth_keyboard_config(billboard)
        all_messages += get_sampler_keyboard_config(billboard)

        # TODO: Used to have keybaord quantization but not sure I want all commands to run on queue
        # TODO: effects mod seems to behave a bit weirdly
        # TODO: Noted that drones don't work at all at present - investigate!
        #all_messages += get_all_effects_mod(billboard)
        all_messages += [get_sequencer_batch_queue_bundle(billboard)]

        for msg in all_messages:
            sleep(0.005) # Seems to be needed to prevent dropped messages
            client.send(msg)

example = "/home/estrandv/programming/jdw-pycompose/songs/courtRide.bbd"
configure(example)
update_queue(example)
