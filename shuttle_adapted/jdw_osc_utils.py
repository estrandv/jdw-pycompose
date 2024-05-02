from pythonosc import osc_message_builder, udp_client, osc_bundle_builder
from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_message import OscMessage
from shuttle_notation import ResolvedElement
from jdw_shuttle_utils import resolve_freq


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
    # TODO: BPM and project output 
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

# TODO: silence is just a bullshit address message with no arg 

def to_note_on(element: ResolvedElement, synth_name: str):
    freq = resolve_freq(element)

    # Just expecting it to be there with this name 
    gate_time = str(element.args["sus"])
    
    # Silly external note id default - not sure what a good other option is if tone is not mandatory 
    ext_id = element.suffix if element.suffix != "" else "no_external_id"

    osc_args = ["freq", freq]
    for key in element.args:
        if key not in ["sus", "freq"]:
            osc_args.append(key)
            osc_args.append(float(element.args[key])) 
    
    return create_msg("/note_on", [synth_name, ext_id, SC_DELAY_MS] + osc_args)

def to_sample_play(element: ResolvedElement, sample_pack: str):
    
    # Silly external note id default - not sure what a good other option is if tone is not mandatory 
    ext_id = element.suffix if element.suffix != "" else "sample" + ",".join(element.args)
    
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

    print("ATTEMPTING MOD WITH ID", external_id, element)

    return create_msg("/note_modify", [external_id, SC_DELAY_MS] + osc_args)

def to_note_on_timed(element: ResolvedElement, synth_name: str):


    freq = resolve_freq(element)

    # Just expecting it to be there with this name 
    gate_time = str(element.args["sus"])
    
    # Silly external note id default - not sure what a good other option is if tone is not mandatory 
    ext_id = element.suffix if element.suffix != "" else "no_external_id"

    osc_args = ["freq", freq]
    for key in element.args:
        if key not in ["sus", "freq"]:
            osc_args.append(key)
            osc_args.append(float(element.args[key])) 
    return create_msg("/note_on_timed", [synth_name, ext_id, gate_time, SC_DELAY_MS] + osc_args)

def to_timed_osc(time: str, osc_packet):
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    bundle.add_content(create_msg("/bundle_info", ["timed_msg"]))
    bundle.add_content(create_msg("/timed_msg_info", [time]))
    bundle.add_content(osc_packet)
    return bundle.build()    
