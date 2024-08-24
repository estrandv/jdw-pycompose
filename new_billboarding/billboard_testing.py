# WIP all-in-one calls to JDW via new billboard


from pythonosc.osc_message import OscMessage
from client import get_default
from new_billboarding.billboard_osc_conversion import get_all_command_messages, get_all_effects_create, get_all_effects_mod, get_sampler_keyboard_config, get_synth_keyboard_config
from new_billboarding.billboarding import parse_billboard

def configure(bdd_path: str):
    with open(bdd_path, 'r') as bdd_file:
        billboard = parse_billboard(bdd_file.read())

        all_messages: list[OscMessage] = []

        all_messages += get_synth_keyboard_config(billboard)
        all_messages += get_sampler_keyboard_config(billboard)
        all_messages += get_all_effects_create(billboard)
        all_messages += get_all_command_messages(billboard)

        for msg in all_messages:
            get_default().send(msg)
