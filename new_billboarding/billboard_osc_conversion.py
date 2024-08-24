from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_message import OscMessage
from pythonosc.osc_packet import OscPacket
from new_billboarding.billboarding import Billboard
from new_billboarding.shuttle_jdw_translation import args_as_osc, create_batch_bundle, create_batch_queue_bundle, create_msg, create_queue_update_bundle, to_timed_osc

def get_synth_keyboard_config(billboard: Billboard) -> list[OscMessage]:

    messages: list[OscMessage] = []

    all_selected = [header.key_configuration for header in billboard.sections if header.key_configuration != None \
        and header.key_configuration.for_sampler == False]

    if len(all_selected) > 0:
        final = all_selected[-1]
        args = args_as_osc(final.args, [])
        messages.append(create_msg("/keyboard_instrument_name", [final.instrument_name]))
        messages.append(create_msg("/keyboard_args", args))

    return messages

def get_sampler_keyboard_config(billboard: Billboard) -> list[OscMessage]:

    messages: list[OscMessage] = []

    all_selected = [header.key_configuration for header in billboard.sections if header.key_configuration != None \
        and header.key_configuration.for_sampler == True]

    if len(all_selected) > 0:
        final = all_selected[-1]
        args = args_as_osc(final.args, [])
        messages.append(create_msg("/keyboard_pad_pack", [final.instrument_name]))
        messages.append(create_msg("/keyboard_pad_args", args))
        if len(final.pads_config) > 0:
            pad_select_osc: list[str | float | int] = []
            for conf in final.pads_config:
                pad_select_osc.append(conf.pad_number)
                pad_select_osc.append(conf.configured_index)
            messages.append(create_msg("/keyboard_pad_samples", pad_select_osc))

    return messages

def get_all_effects_mod(billboard: Billboard) -> list[OscMessage]:
    ret: list[OscMessage] = []
    for section in billboard.sections:
        ret += [e.as_create_osc() for e in section.effects]
    return ret

def get_all_effects_create(billboard: Billboard) -> list[OscMessage]:
    ret: list[OscMessage] = []
    for section in billboard.sections:
        ret += [e.as_create_osc() for e in section.effects]
    return ret

def get_all_command_messages(billboard: Billboard) -> list[OscMessage]:
    ret: list[OscMessage] = []
    for cmd in billboard.commands:
        if cmd.address == "/set_bpm":
            ret.append(create_msg("/set_bpm", [int(cmd.args[0])]))
        if cmd.address == "/keyboard_quantization":
            ret.append(create_msg("/keyboard_quantization", [cmd.args[0]]))

        # TODO: Routers should probably be defined as commands called "raw effect" or smth, then
        # be reated like effects but always read -first-

    return ret

def get_sequencer_batch_queue_bundle(billboard: Billboard) -> OscBundle:
    queue_bundles: list[OscBundle] = []
    for sec in billboard.sections:
        for track_name in sec.tracks:
            track = sec.tracks[track_name]
            timed_sequence = [to_timed_osc(msg.get_time(), msg.osc) for msg in track]
            queue_bundle = create_queue_update_bundle(track_name, timed_sequence)
    return create_batch_queue_bundle(queue_bundles, True)
