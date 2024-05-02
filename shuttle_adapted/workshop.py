from shuttle_notation import Parser, ResolvedElement
from decimal import Decimal
from pythonosc import osc_message_builder, udp_client, osc_bundle_builder

import jdw_osc_utils
import jdw_shuttle_utils
from jdw_shuttle_utils import MessageType

#####################################

"""

This file aims to contain everything needed to parse and send messages to the router. 

Splitting will be done later. 

Current shortcuts taken: 
- Hardcoded message types, synth names or external ids
    -> Only available message type is note_on_timed (see: osc_transform)

LOG:
- Tested OK with note_on_timed!
- Fixed a bug and now it sounds great in sequence
- Moved things around, tested working note mod 
- NRT tested and working for at least note_on_timed
- Samples tested ok for both nrt and real-time, thus finalizing message type support 
- Multi-track syntax tested OK for both nrt and real-time

"""

def create_timed_jdw_messages(elements: list[ResolvedElement], synth_name) -> list:

    sequence = []
    for element in elements:

        msg = None 
        match jdw_shuttle_utils.resolve_message_type(element):
            case MessageType.DEFAULT:

                # Note the convenience hack here - "SP_"-prefix means we're playing a sample pack synth 
                if "SP_" in synth_name:
                    msg = jdw_osc_utils.to_sample_play(element, synth_name.replace("SP_", ""))
                else:
                    msg = jdw_osc_utils.to_note_on_timed(element, synth_name)

            case MessageType.DRONE:
                msg = jdw_osc_utils.to_note_on(element, synth_name)
            case MessageType.NOTE_MOD:
                msg = jdw_osc_utils.to_note_mod(element, "".join(element.suffix[1:])) # TODO: safety 
            case MessageType.EMPTY:
                msg = jdw_osc_utils.create_msg("/empty_msg", [])
            case _:
                pass  

        if msg != None:
            with_time = jdw_osc_utils.to_timed_osc(str(element.args["time"]), msg)    
            sequence.append(with_time)

    return sequence


client = udp_client.SimpleUDPClient("127.0.0.1", 13339) # Router

# TODO: NRT automatically adjusts arg times as beats with BPM 
# I think this might be doable as a message to scsynth live as well
# If not, we should apply timing BEFORE we send 
bpm = 120.0 

parser = Parser()
parser.arg_defaults = {"time": Decimal("0.5"), "sus": Decimal("0.2"), "amp": Decimal("0.5")}

# {synth_name:parse_string}
tracks = {}

# Example regular synth
# Note special jdw characters: "x" is EMPTY, "." is IGNORE/SPACER
#tracks["lead:brute"] = "(c3 . (d3)*4:0.125,sus0.05,relT0 . eb3 . (c4:0 g3 / eb4:relT2.5 / eb4:0 g3 / (c4 / b3):relT2.5)):relT0.8,sus0.01,fx0.83"

# Example sample synth
tracks["drums:SP_Roland808"] = "(bd3 mi1:0,ofs0.05 bd4 (sn3 / sn4) (x / bd7 / x / (to3)*4:0.125)):amp1,ofs0"

for track in tracks:

    name_split = track.split(":")
    track_id = name_split[0]
    synth_name = name_split[1]

    elements = parser.parse(tracks[track])

    sequence = create_timed_jdw_messages(elements, synth_name)

    # Example queue send
    output_bundle = jdw_osc_utils.create_queue_update_bundle(track_id, sequence)

    # Example nrt send 
    file_name = "/home/estrandv/jdw_output/track_" + track_id + ".wav"
    end_time = sum([float(e.args["time"]) for e in elements]) + 4.0 # A little extra 
    #output_bundle = jdw_osc_utils.create_nrt_record_bundle(sequence, file_name, end_time, bpm)

    # TODO: Remaining client methods examplified 
    client.send(output_bundle)