from dataclasses import dataclass
from decimal import Decimal
from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_message import OscMessage
from pythonosc.osc_packet import OscPacket
from billboarding import Billboard
from default_configuration import get_default_samples, get_default_synthdefs
from nrt_scoring import Score
from parsing import BillboardSynthSection, BillboardTrack, CommandContext
from jdw_osc_utils import ElementMessage, args_as_osc, create_batch_bundle, create_batch_queue_bundle, create_msg, create_nrt_record_bundle, create_queue_update_bundle, to_timed_osc


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
        ret += [create_msg("/note_modify", [e.external_id, 0] + e.osc_args) for e in section.effects]
    return ret

def get_all_effects_create(billboard: Billboard) -> list[OscMessage]:
    ret: list[OscMessage] = []
    for section in billboard.sections:
        ret += get_section_effects_create(section)
    return ret

def get_section_effects_create(section: BillboardSynthSection) -> list[OscMessage]:
    return [create_msg("/note_on", [e.synth_name, e.external_id, 0] + e.osc_args) for e in section.effects]

def get_all_command_messages(billboard: Billboard, type_filter: list[CommandContext] = []) -> list[OscMessage]:
    ret: list[OscMessage] = []
    for cmd in billboard.commands:

        if cmd.context in type_filter or len(type_filter) == 0:

            if cmd.address == "/set_bpm":
                ret.append(create_msg("/set_bpm", [int(cmd.args[0])]))
            if cmd.address == "/keyboard_quantization":
                ret.append(create_msg("/keyboard_quantization", [cmd.args[0]]))
            if cmd.address == "/create_router":
                in_arg = float(cmd.args[0])
                out_arg = float(cmd.args[1])
                ext_id = "effect_router_" + str(in_arg) + "_" + str(out_arg)
                ret.append(create_msg("/note_on", ["router", ext_id, 0, "in", in_arg, "out", out_arg]))

    return ret

@dataclass
class NrtBundleInfo:
    track_name: str
    nrt_bundle: OscBundle
    preload_messages: list[OscMessage]

def get_nrt_record_bundles(billboard: Billboard) -> list[NrtBundleInfo]:

    all_bundle_infos: list[NrtBundleInfo] = []

    score = Score()

    # Add tracks to score
    for sec in billboard.sections:
        for track_name in sec.tracks:
            track: BillboardTrack = sec.tracks[track_name]
            score.add_source(track_name, track.group_name, track.messages)

    # Walk through each section of group filters in order to create a chronological score
    for filter_set in billboard.group_filters:
        score.extend_groups(filter_set)

    timed_track_messages: dict[str, list[OscBundle]] = score.unpack_timed_tracks()

    # TODO: Only interested in router commands, maybe a filter is easiest
    # Techincally we would like to use the bpm command as well for the final bpm of the nrt
    command_messages: list[OscMessage] = get_all_command_messages(billboard, [CommandContext.ALL, CommandContext.UPDATE])
    timed_cmd_msgs: list[OscBundle] = [to_timed_osc("0.0", msg) for msg in command_messages]

    # Begin creating the bundles
    for section in billboard.sections:
        timed_eff_msgs: list[OscBundle] = [to_timed_osc("0.0", msg) for msg in get_section_effects_create(section)]

        # Preload messages are messages not part of the bundle but needed before the bundle is sent
        all_preload_messages: list[OscMessage] = [create_msg("/clear_nrt", [])]
        all_setup_messages: list[OscBundle] = timed_cmd_msgs + timed_eff_msgs

        if section.header.is_sampler:
            # Only load samples from the active pack
            # TODO: ODes this work, or will instrument name sitll be "SP_*"?
            sample_load_msgs: list[OscMessage] = [sample.load_msg for sample in get_default_samples() if sample.sample.sample_pack == section.header.instrument_name]
            all_preload_messages += sample_load_msgs

        # TODO: Default synth name parsing is currently broken (names have different formats and the parse is half-finished)
        needed_effect_names: list[str] = [e.synth_name for e in section.effects] + ["sampler", "router"]
        def synth_needed(synth_name) -> bool:
            return section.header.instrument_name == synth_name or synth_name in needed_effect_names
        synth_create_msgs: list[OscMessage] = [synth.load_msg for synth in get_default_synthdefs() if synth_needed(synth.name)]

        all_preload_messages += synth_create_msgs

        # Begin creating track file definitions
        for track_name in section.tracks:
            nrt_track = timed_track_messages[track_name]

            score_bundles = all_setup_messages + nrt_track

            # TODO: Assert that track is not empty or all silent

            # TODO: Bpm from command messagee
            bpm: float = 116.0 # TODO: See notes on current bpm type expectation issues
            file_name: str = "/home/estrandv/jdw_output/track_" + str(track_name) + ".wav"
            end_time: Decimal = score.get_end_time() + Decimal("8.0") # A little extra
            bundle = create_nrt_record_bundle(score_bundles, file_name, float(end_time), bpm)
            bundle_info = NrtBundleInfo(track_name, bundle, all_preload_messages)
            all_bundle_infos.append(bundle_info)

    return all_bundle_infos


def get_sequencer_batch_queue_bundle(billboard: Billboard) -> OscBundle:
    queue_bundles: list[OscBundle] = []
    for sec in billboard.sections:
        for track_name in sec.tracks:
            track = sec.tracks[track_name]

            # Use the last defined group filter for queue updates
            if track.group_name in billboard.get_final_filter() or len(billboard.get_final_filter()) == 0:
                timed_sequence = [to_timed_osc(msg.get_time(), msg.osc) for msg in track.messages]
                queue_bundle = create_queue_update_bundle(track_name, timed_sequence)
                queue_bundles.append(queue_bundle)
    return create_batch_queue_bundle(queue_bundles, True)
