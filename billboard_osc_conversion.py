# Purpose: Creating send-ready OSC data from fully parsed Billboard classes, ideally as pure orchestrations of other lib conversion methods.

from dataclasses import dataclass
from decimal import Decimal
from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_message import OscMessage
from pythonosc.osc_packet import OscPacket
from shuttle_notation.parsing.information_parsing import ElementInformation
from billboard_classes import Billboard
from default_configuration import SampleMessage, get_default_samples, get_default_synthdefs
from nrt_scoring import Score
from billboard_classes import BillboardSynthSection, BillboardTrack, CommandContext
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
    preload_bundles: list[OscBundle]

def _filter_used_samples(all_samples: list[SampleMessage], pack_name: str, track_messages: list[ElementMessage]) -> list[SampleMessage]:
    pack_samples: list[SampleMessage] = [sample for sample in all_samples if sample.sample.sample_pack == pack_name]

    used_samples: list[SampleMessage] = []

    # Replicating the category/index logic used in jdw-sc. Kinda clumsy, but works for a POC ...
    usage_by_category: dict[str, list[int]] = {}

    for msg in track_messages:

        # TODO: THIS CAN BUG: Jdw-sc defaults unknown prefixes to category <blank>, but this won't.
        # Kinda speaks to the fragility of this system, but it's possible that we rework categories in
        # the future, so I'm keeping it here in full display.
        # NOTE: An easy way to avoid category resolution is to just count all categorized samples as used
        # .... ACTUALLY, I think category IS DETERMINED HERE, not in JDW_SC, so we can prob reuse that logic... duh.
        # SO, TODO: First check in the category resolution of default samples if this category is valid or should be ""
        if msg.element.prefix not in usage_by_category:
            usage_by_category[msg.element.prefix] = []

        if msg.element.index not in usage_by_category[msg.element.prefix]:
            usage_by_category[msg.element.prefix].append(msg.element.index)

    for sample in pack_samples:

        category = sample.sample.category if sample.sample.category in usage_by_category else ""
        usage_in_category: list[int] = usage_by_category[category]

        if sample.sample.tone_index in usage_in_category:
            used_samples.append(sample)

    return used_samples

"""

    FAQ

    Q: But why can't we just construct the full scd nrt script here, instead of in jdw-sc, since we know all the data already?
    A: Jdw-sc has a lot of "smart messages", like note_on_timed or play_sample, that we'd have to resolve here as well in that case.
        - This is easier!

    Q: Why do we do so much "nrt preloading" instead of sending everything in the same bundle?
    A: Since NRT recording uses -a lot- of data to compose whole songs of dynamic length, having everything in the same bundle
        can literally make the message too big for your network card.


"""
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

        # TODO: Trying to understand why samplers sound strange in NRT
        timed_eff_msgs: list[OscBundle] = [to_timed_osc("0.0", msg) for msg in get_section_effects_create(section)]
        #timed_eff_msgs: list[OscBundle] = [to_timed_osc("0.0", msg) for msg in get_all_effects_create(billboard)]

        # Preload messages are messages not part of the bundle but needed before the bundle is sent
        all_preload_messages: list[OscMessage] = [create_msg("/clear_nrt", [])]
        all_setup_messages: list[OscBundle] = timed_cmd_msgs + timed_eff_msgs

        # TODO: Default synth name parsing is currently broken (names have different formats and the parse is half-finished)
        needed_effect_names: list[str] = [e.synth_name for e in section.effects] + ["sampler", "router"]
        def synth_needed(synth_name) -> bool:
            #return True
            return section.header.instrument_name == synth_name or synth_name in needed_effect_names
        synth_create_msgs: list[OscMessage] = [synth.load_msg for synth in get_default_synthdefs() if synth_needed(synth.name)]

        all_preload_messages += synth_create_msgs

        # Begin creating track file definitions
        for track_name in section.tracks:

            # Prepare sample loads, if relevant
            if section.header.is_sampler:
                all_samples = get_default_samples()
                # TODO: Bring filtering back
                my_samples = _filter_used_samples(all_samples, section.header.instrument_name, section.tracks[track_name].messages)
                #my_samples = all_samples
                all_preload_messages += [s.load_msg for s in my_samples]

            # Finalize track
            nrt_track = timed_track_messages[track_name]

            score_bundles = all_setup_messages + nrt_track

            # TODO: Assert that track is not empty or all silent

            # TODO: Bpm from command messagee
            bpm: float = 116.0 # TODO: See notes on current bpm type expectation issues
            file_name: str = "/home/estrandv/jdw_output/track_" + str(track_name) + ".wav"
            end_time: Decimal = score.get_end_time() + Decimal("8.0") # A little extra, but still doesn't account properly for release/delay/reverb

            # No score bundles are included in this since it creates too massive bundles, instead we put them in preload
            bundle = create_nrt_record_bundle([], file_name, float(end_time), bpm)
            bundle_info = NrtBundleInfo(track_name, bundle, all_preload_messages, preload_bundles=score_bundles)
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
