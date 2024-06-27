import client as jdw_client
import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils
from dataclasses import dataclass

# DEPRECATED - KEEPING FOR KEYBOARD REIMPLEMENTATION INSPO

def as_synth(octave = 5, synth = "pycompose", quantization = "0.25", args = ["ofs", 0.0, "relT", 2.5, "sus", 0.5, "amp", 1.0]):

    client = jdw_client.get_default()

    client.send(jdw_osc_utils.create_msg("/keyboard_mode_synth"))
    client.send(jdw_osc_utils.create_msg("/keyboard_quantization", [quantization]))
    client.send(jdw_osc_utils.create_msg("/keyboard_instrument_name", [synth]))
    client.send(jdw_osc_utils.create_msg("/keyboard_args", args))
    for char in "q2w3er5t6y7ui9o0p":
        client.send(jdw_osc_utils.create_msg("/keyboard_letter_index", [char, octave]))

def as_sampler(pack = "Roland808", quantization = "0.25", args = ["ofs", 0.0, "relT", 2.5, "sus", 0.5, "amp", 1.0]):

    client = jdw_client.get_default()

    client.send(jdw_osc_utils.create_msg("/keyboard_mode_sampler"))
    client.send(jdw_osc_utils.create_msg("/keyboard_quantization", [quantization]))
    client.send(jdw_osc_utils.create_msg("/keyboard_instrument_name", [pack]))
    client.send(jdw_osc_utils.create_msg("/keyboard_args", args))
    sample_key = 0
    for char in "q2w3er5t6y7ui9o0p":
        client.send(jdw_osc_utils.create_msg("/keyboard_letter_index", [char, sample_key]))
        sample_key += 4
