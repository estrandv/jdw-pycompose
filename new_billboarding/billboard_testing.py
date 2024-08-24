# WIP all-in-one calls to JDW via new billboard


from pythonosc.osc_message import OscMessage
from pythonosc.udp_client import SimpleUDPClient
from billboard_osc_conversion import get_all_command_messages, get_all_effects_create, get_all_effects_mod, get_sampler_keyboard_config, get_synth_keyboard_config
from billboarding import parse_billboard
import os

import temp_import.default_synthdefs as default_synthdefs
import temp_import.sample_reading as sample_reading

from shuttle_jdw_translation import create_msg

def configure(bdd_path: str):
    client = SimpleUDPClient("127.0.0.1", 13339) # Router, should normally just use default

    # TODO: Helper lib to just return the messages for these defaults
    # Might as well tag them, too, so its easier to filter
    for sample in sample_reading.read_sample_packs("~/sample_packs"):
        client.send(create_msg("/load_sample", sample.as_args()))

    synths: list[str] = default_synthdefs.get()
    for synth in synths:
        client.send(create_msg("/create_synthdef", [synth]))

    with open(bdd_path, 'r') as bdd_file:
        billboard = parse_billboard(bdd_file.read())

        all_messages: list[OscMessage] = []

        all_messages += get_synth_keyboard_config(billboard)
        all_messages += get_sampler_keyboard_config(billboard)
        all_messages += get_all_effects_create(billboard)
        all_messages += get_all_command_messages(billboard)

        for msg in all_messages:
            client.send(msg)


here = os.path.dirname(os.path.realpath(__file__))
configure("/home/estrandv/programming/jdw-pycompose/songs/courtRide.bbd")
