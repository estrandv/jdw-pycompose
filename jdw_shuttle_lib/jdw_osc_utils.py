# utilities for converting shuttle elements into jackdaw-compatible OSC messages 

from pythonosc import osc_message_builder, udp_client, osc_bundle_builder
from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_message import OscMessage
from pythonosc.osc_packet import OscPacket
from shuttle_notation import ResolvedElement
from jdw_shuttle_lib.shuttle_jdw_translation import MessageType

from jdw_shuttle_lib.shuttle_jdw_translation import ElementWrapper

# TODO: Pass in, somehow... 
SC_DELAY_MS = 70

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
    sequence: list[OscMessage], # timed 
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

def create_queue_update_bundle(queue_id: str, sequence: list[OscMessage]) -> OscBundle:

    # Building a standard queue_update bundle 
    queue_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    queue_bundle.add_content(create_msg("/bundle_info", ["update_queue"]))
    queue_bundle.add_content(create_msg("/update_queue_info", [queue_id]))

    note_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

    for msg in sequence:
        note_bundle.add_content(msg)

    queue_bundle.add_content(note_bundle.build())

    return queue_bundle.build()

# Basic quick-syntax for OSC message building, ("/s_new, [1,2,3...]")
def create_msg(adr: str, args = []) -> OscMessage:
    builder = osc_message_builder.OscMessageBuilder(address=adr)
    for arg in args:
        builder.add_arg(arg)
    return builder.build()

def to_timed_osc(time: str, osc_packet) -> OscBundle:
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    bundle.add_content(create_msg("/bundle_info", ["timed_msg"]))
    bundle.add_content(create_msg("/timed_msg_info", [time]))
    bundle.add_content(osc_packet)
    return bundle.build()

def resolve_jdw_msg(element: ElementWrapper) -> OscPacket | None:
    external_id = element.resolve_external_id()
    freq = element.resolve_freq()
    msg_type = element.resolve_message_type()

    msg = None 

    match msg_type:
        case MessageType.NOTE_ON_TIMED:
            gate_time = str(element.element.args["sus"])
            osc_args = element.args_as_osc(["freq", freq])
            msg = create_msg("/note_on_timed", [element.instrument_name, external_id, gate_time, SC_DELAY_MS] + osc_args)

        case MessageType.PLAY_SAMPLE:
            msg = create_msg("/play_sample", [external_id, element.instrument_name, element.element.index, element.element.prefix, SC_DELAY_MS] + element.args_as_osc())
        
        case MessageType.DRONE:
            osc_args = element.args_as_osc(["freq", freq])
            msg = create_msg("/note_on", [element.instrument_name, external_id, SC_DELAY_MS] + osc_args)

        case MessageType.NOTE_MOD:
            osc_args = element.args_as_osc(["freq", freq])
            print("DEBUG: Note modify created: \"" + external_id + "\"", osc_args)
            msg = create_msg("/note_modify", [external_id, SC_DELAY_MS] + osc_args)

        case MessageType.EMPTY:
            msg = create_msg("/empty_msg", [])

        case MessageType.LOOP_START_MARKER:
            msg = create_msg("/loop_started", [])
        case _:
            pass

    return msg 

# Resolves the appropriate type of message for the element and returns it, wrapped inside its "time" argument 
def create_sequencer_note(element: ElementWrapper) -> OscBundle | None:

    msg = resolve_jdw_msg(element)

    return to_timed_osc(str(element.element.args["time"]), msg) if msg != None else None 