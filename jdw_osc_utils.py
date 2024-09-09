from dataclasses import dataclass
from decimal import Decimal
from pythonosc.osc_message import OscMessage
from pythonosc.osc_packet import OscPacket
from shuttle_notation.parsing.information_parsing import DynamicArg
import note_utils as note_utils
from enum import Enum
from pretty_midi import note_number_to_hz

from line_classify import begins_with
from pythonosc import osc_message_builder, udp_client, osc_bundle_builder
from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_message import OscMessage
from pythonosc.osc_packet import OscPacket
from shuttle_notation import ResolvedElement
from billboard_classes import ElementMessage

# TODO: Pass in, somehow...
SC_DELAY_MS = 70

def create_nrt_preload_bundle(content: list[OscBundle]) -> OscBundle:

    content_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    content_bundle.add_content(create_msg("/bundle_info", ["nrt_preload"]))

    nested_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    for cnt in content:
        content_bundle.add_content(cnt)

    #content_bundle.add_content(nested_bundle.build())

    return content_bundle.build()

def create_batch_queue_bundle(queues: list[OscBundle], stop_missing: bool) -> OscBundle:
    queue_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    queue_bundle.add_content(create_msg("/bundle_info", ["batch_update_queues"]))
    queue_bundle.add_content(create_msg("/batch_update_queues_info", [1 if stop_missing else 0]))

    nested_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    for queue in queues:
        nested_bundle.add_content(queue)

    queue_bundle.add_content(nested_bundle.build())

    return queue_bundle.build()

def create_nrt_record_bundle(
    sequence: list[OscBundle], # timed
    file_name: str,
    end_time: float,
    bpm: float = 120.0 # TODO: Fix type when the expectation in jdw-sc is corrected
) -> OscBundle:

    main_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    note_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

    for timed_message in sequence:
        note_bundle.add_content(timed_message)

    main_bundle.add_content(create_msg("/bundle_info", ["nrt_record"]))
    main_bundle.add_content(create_msg("/nrt_record_info", [bpm, file_name, end_time]))
    main_bundle.add_content(note_bundle.build())

    return main_bundle.build()

def create_queue_update_bundle(queue_id: str, timed_osc_msgs: list[OscBundle]) -> OscBundle:

    # Building a standard queue_update bundle
    queue_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    queue_bundle.add_content(create_msg("/bundle_info", ["update_queue"]))
    queue_bundle.add_content(create_msg("/update_queue_info", [queue_id]))

    note_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

    for msg in timed_osc_msgs:
        note_bundle.add_content(msg)

    queue_bundle.add_content(note_bundle.build())

    return queue_bundle.build()

def create_batch_bundle(packets: list[OscPacket]) -> OscBundle:
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    bundle.add_content(create_msg("/bundle_info", ["batch-send"]))
    for packet in packets:
        bundle.add_content(packet)

    return bundle.build()

# Basic quick-syntax for OSC message building, ("/s_new, [1,2,3...]")
def create_msg(adr: str, args: list[str | float | int] = []) -> OscMessage:
    builder = osc_message_builder.OscMessageBuilder(address=adr)
    for arg in args:
        builder.add_arg(arg)
    return builder.build()

def to_timed_osc(time: str, osc_packet: OscMessage | OscPacket) -> OscBundle:
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    bundle.add_content(create_msg("/bundle_info", ["timed_msg"]))
    bundle.add_content(create_msg("/timed_msg_info", [time]))
    bundle.add_content(osc_packet)
    return bundle.build()

def is_symbol(element: ResolvedElement, sym: str) -> bool:
    return element.suffix.lower() == sym \
        and element.prefix == "" \
        and element.index == 0

def resolve_external_id(element: ResolvedElement) -> str:
    resolved = element.suffix
    return resolved if resolved != "" else "id_" + str(element.index)

def resolve_freq(element: ResolvedElement) -> float:

    if "freq" in element.args:
        return float(element.args["freq"])

    letter_check = note_utils.note_letter_to_midi(element.prefix)

    if letter_check == -1:

        # Placeholders
        # TODO: Complete bullshit, but helps with keybaoard usage for now
        #octave = 0 if element.index > 12 else 3
        octave = 0

        extra = (12 * (octave + 1)) if octave > 0 else 0
        new_index = element.index + extra
        # TODO: port transpose from scales.py
        #   Implied scale: Chromatic
        #scale = scales.MAJOR
        #new_index = transpose(new_index, scale)
        freq = note_number_to_hz(new_index)
        return freq

    else:
        # E.g. "C" or "C#" or "Cb"
        letter_and_semitone = element.prefix.lower()
        # As in the "3" of "c3"
        octave = element.index if element.index != None else 1

        # Math, same as for index freq calculation
        extra = (12 * (octave - 1)) if octave > 0 else 0
        new_index = letter_check + extra

        return note_number_to_hz(new_index)

def args_as_osc(raw_args: dict[str, Decimal], override: list[str | float]):
    osc_args: list[str | float] = []

    for arg in override:
        osc_args.append(arg)

    for arg in raw_args:
        if arg not in osc_args:
            osc_args.append(arg)
            osc_args.append(float(raw_args[arg]))
    return osc_args



# Some elements have symbols or other syntax that force a certain osc format
def resolve_special_message(element: ResolvedElement, instrument_name: str) -> ElementMessage | None:
    if begins_with(element.suffix, "@"):
        # Remove symbol from suffix to create note mod external id
        return ElementMessage(element, to_note_mod(element, cut_first(element.suffix, 1)))
    elif is_symbol(element, "x"):
        # Silence
        return ElementMessage(element, create_msg("/empty_msg", []))
    elif is_symbol(element, "."):
        # Ignore
        pass
    elif is_symbol(element, "§"):
        # Loop start marker
        return ElementMessage(element, create_msg("/loop_started", []))
    elif begins_with(element.suffix, "$"):
        # Drone, note that suffix is trimmed similar to for note mod
        return ElementMessage(element, to_note_on(element, instrument_name, cut_first(element.suffix, 1)))

    return None

def to_note_mod(element: ResolvedElement, external_id_override: str = "") -> OscMessage:
    external_id = resolve_external_id(element) if external_id_override == "" else external_id_override
    osc_args = args_as_osc(element.args, ["freq", resolve_freq(element)])
    return create_msg("/note_modify", [external_id, SC_DELAY_MS] + osc_args)

def to_note_on_timed(element: ResolvedElement, instrument_name: str) -> OscMessage:
    freq = resolve_freq(element)
    external_id = resolve_external_id(element)

    sus: float = element.args["sus"] if "sus" in element.args else 0.0
    if sus == 0.0:
        print("WARN: Element converted to timed note press did not contain a sus arg (will be 0.0): ", element)

    gate_time = str(sus)
    osc_args = args_as_osc(element.args, ["freq", freq])
    return create_msg("/note_on_timed", [instrument_name, external_id, gate_time, SC_DELAY_MS] + osc_args)

def to_play_sample(element: ResolvedElement, instrument_name: str) -> OscMessage:
    osc_args = args_as_osc(element.args, ["freq", resolve_freq(element)])
    return create_msg("/play_sample", [
        resolve_external_id(element), instrument_name, element.index, element.prefix, SC_DELAY_MS
    ] + osc_args)

def to_note_on(element: ResolvedElement, instrument_name: str, external_id_override: str = "") -> OscMessage:
    external_id = resolve_external_id(element) if external_id_override == "" else external_id_override
    freq = resolve_freq(element)
    osc_args = args_as_osc(element.args, ["freq", freq])
    return create_msg("/note_on", [instrument_name, external_id, SC_DELAY_MS] + osc_args)
