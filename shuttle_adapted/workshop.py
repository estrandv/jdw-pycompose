from shuttle_notation import Parser, ResolvedElement
from decimal import Decimal
from pythonosc import osc_message_builder, udp_client, osc_bundle_builder

import jdw_osc_utils
import jdw_shuttle_utils
from jdw_shuttle_utils import MessageType

#####################################

"""

This file aims to contain everything needed to parse and send messages to the router. 


FEATURE BRAINSTORM:
    - Effects! 
        - Seems busses can't be created with OSC - "b = Bus.audio(server, 1);"
            - Supposedly you have some control over the index, too, if that matters
        - s_new has grouping and "add_actions" that supposedly help with ordering
            - So -when- you change to a bus as out does nto matter
            - Neither does the timing of the -creation- of the bus
            - But when several synths interact via a common bus, there is an order
            - As I recall, there are tricks to this 
                - So for example: all effects would go in a certain group (0), while all synths then go in (1), meaning
                    no matter how you space it, synths are always counted as -after- all effects in any chains 

            SynthDef("reverb",
            {|amp=1, inBus=0, outBus=0|
                snd = In.ar(inBus,1);
                Out.ar(outBus,snd)
            })

            - It's coming back to me! So you want a particular inBus, typically, that your synths target. 
                - Then an effect is reading from that inBus (so effects have to be -after- synths!)
                - And then you always set outBus to "0" because that's the sound card output

            - There are a million different ways to do this, but I think it would be simplest to: 
                a. Have a message that creates buses, or just a preloaded set of like ten buses
                    -> This is the only part that might need some tweaking to work with NRT (but I seem to have an example in the template file)  
                b. Create effects like above with a simple create_synthdef call (remember: no buses or groups required yet!)
                c. Run simple drone note-on calls to init effects for particular buses 
                    -> We should have a call for this anyway! 


        - TODO: 
            1. bus stack and an "assert buses" call that makes sure a certain amount of buses are loaded 
                - I've added a hardcode of bus creations in the NRT script, via native loop which is clean 
                - There seems to be some buses available from the get go, as bus 4 was usable as a reverb bus 
                - Verified that an effect synth (note_on) should be started -before- any other synths (note_on) are created



        - IDEA: Control buses as a way of running mods on as-yet-fired sequenced notes
            - previously planned as a middleman microservice, but it could be doable native! 

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


# Create a drone (here, an effect via bus)
#client.send(jdw_osc_utils.create_msg("/note_on", ["reverb", "reverb_effect_2", 0, "inBus", 4.0, "outBus", 0.0]))
client.send(jdw_osc_utils.create_msg("/note_modify", ["reverb_effect_2", 0, "mix", 0.44, "room", 0.75]))
#client.send(jdw_osc_utils.create_msg("/note_on", ["pycompose", "drone", 0, "bus", 4.0, "amp", 1.0, "sus", 10.0]))


# {synth_name:parse_string}
tracks = {}

# Example regular synth
# Note special jdw characters: "x" is EMPTY, "." is IGNORE/SPACER
#tracks["chords:pycompose"] = "(d4:8,attT0.5 g4:0,attT0.3 (b4 / c4 / a4 / d3):0,attT0.1,relT6):sus2,relT4,amp1,fx0.5"
#tracks["hum:pluck"] = "(g6:0 d5 c5 d5 (b5 / a5) d5 x g5:4):2,relT4,fx0.5,amp1"

#tracks["bass:pycompose"] = "(g3:relT2,attT0.2 x x g3 . g3 x x g3 . x x g3 x . x x (g3 / b3 / c3 / b3) x):0.25,relT0.05,sus0.1"
#tracks["bass:dbass"] = "(g2:relT2,attT0.2 x x g2 . g2 x x g2 . x x g2 x . x x (g2 / b2 / c2 / b2) x):0.25,relT0.2,sus0.1"
#tracks["dee:pluck"] = "(x (x / c5) x d5 b4 x g4 x):0.5,relT0.3,bus4"

#tracks["gba:SP_RP200"] = "(2 2 3 x 2 x (3 / 8) (x / 8)):0.5,ofs0.02,amp1"
#tracks["basicbass:pycompose"] = "(g2*8 d3*8 eb3*8 c3*8):0.5,sus0.3,relT0.5"
tracks["basicbass:pycompose"] = "(g2):0.5,sus0.3,relT0.5"
#tracks["basicbass2:pycompose"] = "(g1*8 d1*8 eb1*8 c1*8):0.5,sus0.1,relT0.1"
#tracks["basicbass3:pycompose"] = "(g4*8 d4*8 eb4*8 c4*8):0.5,sus0.1,relT0.005,amp0.2"
#tracks["dee:pycompose"] = "(x (x / c6) x d5 g6 x g5 x):0.5,relT0.3"
tracks["hum:pycompose"] = "(g6:0 d5 c5 d5 (g5 / a5) d5 x g5:4):2,relT4,fx0.5,amp1"

#tracks["drums:SP_[KB6]_EMU_E-Drum"] = "(bd3 mi1:0,ofs0.05 bd4 (mi40:0 sn3 / sn4) (x / bd7 / x / (to3)*4:0.125)):amp0.4,ofs0,bus4"
#tracks["somedrum:SP_[KB6]_EMU_E-Drum"] = "(17 (1 / 1 / 1 / (3 1):0.25) (12 / 12 / 12 / (12 x 12 12):0.125) (2 / 93)):ofs0,bus4"
tracks["somedrum:SP_[KB6]_EMU_E-Drum"] = "(12 x 17 x 12 12 17 (x / 12)):ofs0,bus4,amp1"
#tracks["somedrum:SP_[KB6]_EMU_E-Drum"] = "(12 x x x 17 x x x):ofs0,bus4,amp1"


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