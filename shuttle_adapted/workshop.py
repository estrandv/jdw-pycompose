from shuttle_notation import Parser, ResolvedElement
from decimal import Decimal

from pythonosc import osc_message_builder, udp_client, osc_bundle_builder

from pretty_midi import note_number_to_hz


SC_DELAY_MS = 70

def note_letter_to_midi(note_string) -> int:
    # https://stackoverflow.com/questions/13926280/musical-note-string-c-4-f-3-etc-to-midi-note-value-in-python
    # [["C"],["C#","Db"],["D"],["D#","Eb"],["E"],["F"],["F#","Gb"],["G"],["G#","Ab"],["A"],["A#","Bb"],["B"]]
    note_map = {
        "c": 0,
        "c#": 1,
        "db": 1,
        "d": 2,
        "d#": 3,
        "eb": 3,
        "e": 4,
        "f": 5,
        "f#": 6,
        "gb": 6,
        "g": 7,
        "g#": 8,
        "ab": 8,
        "a": 9,
        "a#": 10,
        "bb": 10,
        "b": 11
    }

    if note_string in note_map:
        return note_map[note_string]
    else:
        return -1

# Basic quick-syntax for OSC message building, ("/s_new, [1,2,3...]")
def create_msg(adr: str, args = []):
    builder = osc_message_builder.OscMessageBuilder(address=adr)
    for arg in args:
        builder.add_arg(arg)
    return builder.build()

def resolve_freq(element: ResolvedElement) -> Decimal:
    if "freq" in element.args:
        return element.args["freq"]
    
    letter_check = note_letter_to_midi(element.prefix)

    if letter_check == -1:

        # Placeholders 
        octave = 3
        scale = scales.MAJOR

        extra = (12 * (octave + 1)) if octave > 0 else 0
        new_index = element.index + extra
        freq = note_number_to_hz(transpose(new_index, scale))
        return freq 

    else:
        # E.g. "C" or "C#" or "Cb"
        letter_and_semitone = element.prefix.lower() 
        # As in the "3" of "c3"
        octave = element.index if element.index != None else 1

        # Math, same as for index freq calculation
        extra = (12 * (octave + 1)) if octave > 0 else 0
        new_index = letter_check + extra

        return note_number_to_hz(new_index)

def to_note_on_timed(element: ResolvedElement):

    # Just something! 
    synth = "brute"

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
    return create_msg("/note_on_timed", [synth, ext_id, gate_time, SC_DELAY_MS] + osc_args)

def to_timed_osc(time: str, osc_packet):
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    bundle.add_content(create_msg("/bundle_info", ["timed_msg"]))
    bundle.add_content(create_msg("/timed_msg_info", [time]))
    bundle.add_content(osc_packet)
    return bundle.build()    

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

elements = parser.parse("(a3*6:0.25,sus0.1 (c4 / d4 / eb4 / d4):relT1,attT0.2):relT0.2")

#print("  -  ".join([e.to_str() for e in elements]))

queue_id = "my_queue"

# Building a standard queue_update bundle 
queue_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
queue_bundle.add_content(create_msg("/bundle_info", ["update_queue"]))
queue_bundle.add_content(create_msg("/update_queue_info", [queue_id]))

note_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

for element in elements:
    note_on = to_note_on_timed(element)
    with_time = to_timed_osc(str(element.args["time"]), note_on)    
    note_bundle.add_content(with_time)

queue_bundle.add_content(note_bundle.build())

# From jdw_client
client = udp_client.SimpleUDPClient("127.0.0.1", 13339) # Router
client.send(queue_bundle.build())
