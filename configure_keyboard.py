import client as jdw_client
import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils

def as_synth():

    client = jdw_client.get_default()

    client.send(jdw_osc_utils.create_msg("/keyboard_mode_synth"))
    client.send(jdw_osc_utils.create_msg("/keyboard_quantization", ["0.01"]))
    client.send(jdw_osc_utils.create_msg("/keyboard_instrument_name", ["pycompose"]))
    client.send(jdw_osc_utils.create_msg("/keyboard_args", ["ofs", 0.0, "relT", 0.5, "sus", 0.5, "amp", 1.0, "bus", 4.0]))
    octave = 5
    for char in "q2w3er5t6y7ui9o0p":
        client.send(jdw_osc_utils.create_msg("/keyboard_letter_index", [char, octave]))

def as_sampler():

    client = jdw_client.get_default()

    client.send(jdw_osc_utils.create_msg("/keyboard_mode_sampler"))
    client.send(jdw_osc_utils.create_msg("/keyboard_quantization", ["0.125"]))
    client.send(jdw_osc_utils.create_msg("/keyboard_instrument_name", ["Roland808"]))
    client.send(jdw_osc_utils.create_msg("/keyboard_args", ["ofs", 0.0, "relT", 0.5, "sus", 0.5, "amp", 1.0]))
    sample_key = 0
    for char in "q2w3er5t6y7ui9o0p":
        client.send(jdw_osc_utils.create_msg("/keyboard_letter_index", [char, sample_key]))
        sample_key += 4
