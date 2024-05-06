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

# Early example of adding custom synths that work for NRT as well:
# Note the expected format, with no operation at the end
local_synth = """
SynthDef("pycompose",
{|amp=1, sus=0.2, pan=0, bus=0, freq=440, cutoff=1000, rq=0.5, fmod=1, relT=0.04, fxa=1.0, fxf=300, fxs=0.002|
	var osc1, osc2, filter, filter2, env, filterenv, ab;
	amp = amp * 0.2;
	freq = freq * fmod; 
	
	osc1 = Saw.ar(freq);
	osc2 = Mix(Saw.ar(freq * [0.125,1,1.5], [0.5,0.4,0.1]));
	osc2 = Mix(Saw.ar(freq * 2) * [fxs, 0.1], osc2);

	filterenv = EnvGen.ar(Env.adsr(0.0, 0.5, 0.2, sus), 1, doneAction:Done.none);
	filter =  RLPF.ar(osc1 + osc2, cutoff * filterenv + 100, rq);
	ab = abs(filter);
	filter2 = (filter * (ab + 2) / (filter ** 2 + 1 * ab + 1));
	filter2 = BLowShelf.ar(filter2, fxf, fxa, -12);
	filter2 = BPeakEQ.ar(filter2, 1600, 1.0, -6);

	env = EnvGen.ar(Env([0,1,0.8,0.8,0], [0.01, 0, sus, relT]), doneAction:Done.freeSelf);

	Out.ar(bus,Pan2.ar((filter + filter2) * env * amp, pan))
})
"""
client.send(jdw_osc_utils.create_msg("/create_synthdef", [local_synth]))

# TODO: NRT automatically adjusts arg times as beats with BPM 
# I think this might be doable as a message to scsynth live as well
# If not, we should apply timing BEFORE we send 
bpm = 120.0 

# BPM set example
#client.send(create_msg("/set_bpm", [bpm]))

# Stop sequencer example
#client.send(create_msg("/hard_stop", []))

# Wipe on finish example
client.send(jdw_osc_utils.create_msg("/wipe_on_finish"))

# Custom scd example
#with open("synthdefs/pycompose.scd", "r") as file:
#    data = file.read() 
#    client.send(create_msg("/read_scd", [data]))

parser = Parser()
parser.arg_defaults = {"time": Decimal("0.5"), "sus": Decimal("0.2"), "amp": Decimal("0.5")}

# {synth_name:parse_string}
tracks = {}

# Example regular synth
# Note special jdw characters: "x" is EMPTY, "." is IGNORE/SPACER
tracks["chords:pycompose"] = "(d4:8,attT0.5 g4:0,attT0.3 (b4 / c4 / a4 / d3):0,attT0.1,relT6):sus2,relT4,amp0.2,fx0.5"
#tracks["hum:pluck"] = "(g6:0 d5 c5 d5 (b5 / a5) d5 x g5:4):2,relT4,fx0.5,amp1"

#tracks["bass:pycompose"] = "(g3:relT2,attT0.2 x x g3 . g3 x x g3 . x x g3 x . x x (g3 / b3 / c3 / b3) x):0.25,relT0.05,sus0.1"
#tracks["bass:dbass"] = "(g2:relT2,attT0.2 x x g2 . g2 x x g2 . x x g2 x . x x (g2 / b2 / c2 / b2) x):0.25,relT0.2,sus0.1"
#tracks["dee:pluck"] = "(x (x / c5) x d5 b4 x g4 x):0.5,relT0.3"

#tracks["gba:SP_RP200"] = "(2 2 3 x 2 x (3 / 8) (x / 8)):0.5,ofs0.02,amp1"
#tracks["basicbass:pycompose"] = "(g2*8 d3*8 eb3*8 c3*8):0.5,sus0.3,relT0.5"
#tracks["basicbass2:pycompose"] = "(g1*8 d1*8 eb1*8 c1*8):0.5,sus0.1,relT0.1"
#tracks["basicbass3:example"] = "(g4*8 d4*8 eb4*8 c4*8):0.5,sus0.1,relT0.005,amp0.2"
#tracks["dee:pycompose"] = "(x (x / c6) x d5 g6 x g5 x):0.5,relT0.3"
#tracks["hum:pycompose"] = "(g6:0 d5 c5 d5 (g5 / a5) d5 x g5:4):2,relT4,fx0.5,amp1"

#tracks["somedrum:SP_[KB6]_EMU_E-Drum"] = "(17 (1 / 1 / 1 / (3 1):0.25) (12 / 12 / 12 / (12 x 12 12):0.125) (2 / 93)):ofs0"

# Example sample synth
#tracks["drums:SP_Roland808"] = "(bd3 mi1:0,ofs0.05 bd4 (mi40:0 sn3 / sn4) (x / bd7 / x / (to3)*4:0.125)):amp1,ofs0"
#tracks["nd:SP_Roland808"] = "((bd2:0 bd4 x x x x x to2 x . sn3 x x x sn5 x x x)*7 bd4 x x x mi4 x to2 x (sn4*4):0.25,ofs0.05,amp2 ):0.125,ofs0,amp1"

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

    client.send(output_bundle)


    """
    
    ALTERNATIONS QUIRK 

    a3 (f / g / e) -> a3 f a3 g a3 e
    (a3 (f / g / e))*3 -> a3 f a3 g a3 e
    ... which makes complete sense, but gets annoying when you want to do long-section repeats ...
    Some ideas: 
        - Alternative symbol, such as the old section marker, which repeats -after- unwrapping
            -> This can be done in post rather easily and does not have to be in shuttle (but could)
            -> Worth noting is "repeat since beginning" vs "repeat since last section" 
        - Track-repeats in code, which is technically a requirement for more advanced composition anyway 
            -> Thing is, however, that NRT+DAW will always be easier than that 

    JAM BRAINSTORMING
    - Samples ordered by tone can be played as midi if we perform octave and midi conversion from letters 
        - Would take some tweaking to the osc conversion method 


    """