# utilities for converting shuttle elements into jackdaw-compatible OSC messages 

from pythonosc import osc_message_builder, udp_client, osc_bundle_builder
from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_message import OscMessage
from shuttle_notation import ResolvedElement
from jdw_shuttle_lib.jdw_shuttle_utils import resolve_freq, MessageType, resolve_external_id
import jdw_shuttle_lib.jdw_shuttle_utils as jdw_shuttle_utils

# TODO: Pass in, somehow... 
SC_DELAY_MS = 70

def create_nrt_record_bundle(
    sequence: list[OscMessage], # timed 
    file_name: str,
    end_time: float, 
    bpm: float = 120.0 # TODO: Fix type when the expectation in jdw-sc is corrected
):

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
def create_msg(adr: str, args = []):
    builder = osc_message_builder.OscMessageBuilder(address=adr)
    for arg in args:
        builder.add_arg(arg)
    return builder.build()

def to_note_on(element: ResolvedElement, synth_name: str):
    freq = resolve_freq(element)

    # Just expecting it to be there with this name 
    gate_time = str(element.args["sus"])

    osc_args = ["freq", freq]
    for key in element.args:
        if key not in ["sus", "freq"]:
            osc_args.append(key)
            osc_args.append(float(element.args[key])) 
    
    return create_msg("/note_on", [synth_name, resolve_external_id(element), SC_DELAY_MS] + osc_args)

def to_sample_play(element: ResolvedElement, sample_pack: str):

    ext_id = resolve_external_id(element)
    
    osc_args = []
    for key in element.args:
        osc_args.append(key)
        osc_args.append(float(element.args[key]))
    return create_msg("/play_sample", [ext_id, sample_pack, element.index, element.prefix, SC_DELAY_MS] + osc_args)

def to_note_mod(element: ResolvedElement, external_id: str):
   
    freq = resolve_freq(element)
   
    osc_args = ["freq", freq]
    for key in element.args:
        if key != "freq":
            osc_args.append(key)
            osc_args.append(float(element.args[key]))

    return create_msg("/note_modify", [external_id, SC_DELAY_MS] + osc_args)

def to_note_on_timed(element: ResolvedElement, synth_name: str):

    freq = resolve_freq(element)

    # Just expecting it to be there with this name 
    gate_time = str(element.args["sus"])
    
    osc_args = ["freq", freq]
    for key in element.args:
        if key not in ["sus", "freq"]:
            osc_args.append(key)
            osc_args.append(float(element.args[key])) 
    return create_msg("/note_on_timed", [synth_name, resolve_external_id(element), gate_time, SC_DELAY_MS] + osc_args)

def to_timed_osc(time: str, osc_packet):
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    bundle.add_content(create_msg("/bundle_info", ["timed_msg"]))
    bundle.add_content(create_msg("/timed_msg_info", [time]))
    bundle.add_content(osc_packet)
    return bundle.build()

# Default_as_sample was "SP_ in synth_name"
def to_jdw_note_message(element: ResolvedElement, synth_name, default_as_sample=False) -> OscBundle | None:

        msg = None 
        match jdw_shuttle_utils.resolve_message_type(element):
            case MessageType.DEFAULT:

                if default_as_sample:
                    msg = to_sample_play(element, synth_name)
                else:
                    msg = to_note_on_timed(element, synth_name)

            case MessageType.DRONE:
                msg = to_note_on(element, synth_name)
            case MessageType.NOTE_MOD:
                msg = to_note_mod(element, resolve_external_id(element))
            case MessageType.EMPTY:
                msg = create_msg("/empty_msg", [])
            case _:
                pass  

        if msg != None:
            msg = to_timed_osc(str(element.args["time"]), msg)    

        return msg 
