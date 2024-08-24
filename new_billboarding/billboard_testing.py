# WIP all-in-one calls to JDW via new billboard


from pythonosc.osc_message import OscMessage
from pythonosc.udp_client import SimpleUDPClient
from billboard_osc_conversion import get_all_command_messages, get_all_effects_create, get_all_effects_mod, get_sampler_keyboard_config, get_synth_keyboard_config
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

        all_messages += [sample.load_msg for sample in get_default_samples()]
        all_messages += [synth.load_msg for synth in get_default_synthdefs()]

        all_messages += get_synth_keyboard_config(billboard)
        all_messages += get_sampler_keyboard_config(billboard)

        all_messages += [get_effects_clear()]
        all_messages += get_all_command_messages(billboard)
        all_messages += get_all_effects_create(billboard)

        for msg in all_messages:
            client.send(msg)


configure("/home/estrandv/programming/jdw-pycompose/songs/courtRide.bbd")
