from shuttle_notation import Parser, ResolvedElement
from decimal import Decimal
from note_utils import resolve_freq
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

"""

parser = Parser()
parser.arg_defaults = {"time": Decimal("0.5"), "sus": Decimal("0.2"), "amp": Decimal("0.5")}

elements = parser.parse("(c3 (d3*4):0.125,sus0.05,relT0 eb3 (c4:0 g3 / eb4:relT2.5 / eb4:0 g3 / (c4 / b3):relT2.5)):relT0.8,sus0.01,fx0.83")

#print("  -  ".join([e.to_str() for e in elements]))

sequence = []
for element in elements:

    msg = jdw_osc_utils.create_msg("/empty_msg", [])
    match jdw_shuttle_utils.resolve_message_type(element):
        case MessageType.DEFAULT:
            msg = jdw_osc_utils.to_note_on_timed(element, "brute")
        case MessageType.DRONE:
            msg = jdw_osc_utils.to_note_on(element, "brute")
        case MessageType.NOTE_MOD:
            msg = jdw_osc_utils.to_note_mod(element, "".join(element.suffix[1:])) # TODO: safety 
        case _:
            print("OMG")
            pass  

    with_time = jdw_osc_utils.to_timed_osc(str(element.args["time"]), msg)    
    sequence.append(with_time)

queue_bundle = jdw_osc_utils.create_queue_update_bundle("queue_id", sequence)

# From jdw_client
client = udp_client.SimpleUDPClient("127.0.0.1", 13339) # Router
client.send(queue_bundle)
