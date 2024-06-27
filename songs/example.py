from pythonosc.osc_packet import OscPacket
import time
from decimal import Decimal

import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils
from shuttle_notation import Parser, ResolvedElement
import sample_reading
import default_synthdefs

import client as my_client

import billboarding


"""

# Billboard Cheat Sheet (tracks)

### Billboard quirks
# Tracks are named based on their line index and should not be moved around after being defined

### Billboard symbols 
# '@' denotes 'use this synth for below lines' - a string of default args can be provided after
#   - ':' after the synth name provides a GROUP to be used by all below lines (unless provided as <...>)
# '*@' denotes 'configure keyboard to use this synth and these args', a pad configuration string can be set after the args
# '#' denotes comment line
# '<...>' as first text denotes meta-data (see separate note)
# '>>>1 2 fish' defines which groups should be included (others behave as if commented)
# 'backslash' COMBINES LINES natively in python
# '€' denotes effects, e.g. '€reverb room0.2,mix0.4' creates a note_on for a synth named 'reverb'. Default args apply. 

### Meta-data
# Outlined as <group;arg_override> or simply <group>
# Group interacts with group filter, while arg_override is an arg string that is applied to all notes after parsing
#   e.g. "sus+2,amp1.0"

### Note symbols 
# '§' denotes loop start time for keyboard
# 'x' denotes an empty message; silence
# '.' is ignored by the parser
# '$' denotes droning; the note will be set to on with no automated off call 
# '@' denotes modding an existing note with the suffix as id

"""


effect_billboard = """

# EFFECT ORDERING: 
# Assuming default s_new strategy (0): "add to head of group" 
# 1. Routers should be specified first (so as to be processed last)
# 2. Effects second
# Generally: In.ar(other) must be processed after (other)
# And with "add to head" that means "TYPE READERS BEFORE THEIR WRITERS"

# Routers created first, so as to appear last
@router tone:in10,out0
@router ttwo:in20,out0
@router tthr:in30,out0
@router tfou:in40,out0
@router tfiv:in50,out0
@router tsix:in60,out0
@router tsev:in70,out0

# TRYING TO FIND ARGS THAT CHANGE THE MISSING BITS 
@router routerrails:ofs0,sus10,amp1,bus80,in80,out0

@router tnin:in90,out0

"""

# TODO: DEPRECATED
keyboard_config = """

#################
# K E Y B O A R D [¤]
#################

@synth eBass:amp4,cutoff200,susT0.1,relT0.1
@synth moogBass:amp0.02,susT1.1,out90,chorus1.4
#@synth FMRhodes:amp1,susT1.1,chorus0.4
#@synth dBass:amp1,susT1.1,chorus0.4,rate0.125
#@synth prophet:amp1,susT0.5
@synth organReed:amp1,susT0.5
#@synth pluck:amp1,susT0.4,out20
#@synth blip:amp1,susT2

#@synth aPad:amp1


#@sampler EMU_Proteus:ofs0,sus10,amp1
#@sampler EMU_EDrum:ofs0,sus10,amp1
@sampler EMU_SP12:ofs0,sus10,amp1,bus10
@pads 1:0 2:4 3:8 4:12 5:16 6:20 7:24 8:28


#@sampler Roland808:ofs0,sus10,amp1
#@pads 1:0 2:14 3:26 4:32 5:54 6:60 7:70 8:95
"""


billboard = """

#############
# T R A C K S ¶
#############

# REMINDERS:
# - Pick a lead and make it LOUD. It's easy to get stuck in amp0.02. 
# - Good drums can carry the whole thing. Too many instruments is hard to mix.
# - Use effects to mix, avoid tweaking amp in the tracks too much. 
# - Split snares from bassdrums for mixing, they use different freq ranges. 

# BASS DRUM COURT RIDE

>>> drum
#>>> drum keys
>>> drum keys bass cele cymbal
>>> drum keys bass reed cymbal
>>> drum keys bass prophet cymbal boom
>>> drum keys bass rails cymbal boom
#>>> drum keys cele cymbal
#>>> drum bass keys reed cymbal
#>>> drum bass keys prophet reed cymbal
#>>> drum keys boom
#>>> drum keys bass rails cymbal
#>>> drum keys cele boom
#>>> keys reed prophet insanity cymbal
#>>> drum keys reed prophet insanity boom


@prophet
@blip
@ksBass
@dBass
@eBass

@moogBass:prophet susT0.5,sus0.01,amp1,lfoS2,cutoff4000,pan-0.1,out50


    (x:1,fish0 c6:1 e6:1 f6:1 e6:0,susT2 x:12):0.5

    # TODO: Separate unique id ordering for fx/tracks    
    €delay bus50,echo0.25,echt4
    €reverb bus50,room0.9,mix0.9,mul0.8
    €clamp bus50,under6200,over1780



# TODO: Separate
@FMRhodes:keys
    
    (c5:4 c5:4 bb4:4 a4:2 bb4:2):chorus0.4,susT1.1,amp1,time0.5,sus4,len4.0,tot0.00,pan-0.2

    <cele;out20> ((c6:1 bb6:1 a6:0.5 g6:1.5 f6:1 g6:0.5 a6:1 f6:0.5 g6:0 x:0.5 x:0.5)*3 \
        (c6:1 bb6:1 a6:0.5 g6:1.5 x:1 x:0.5 x:1 x:0.5 x:0 x:1)):sus0.25,chorus0.5,relT0.8,amp0.4,cutoff1000,len8,tot7.00,pan0.3

@pluck:insanity out20

    €reverb bus20,room0.8,mix0.7,mul0.8
    €clamp bus20,under1500,over880

    (c7:1 c8:0.5 bb7:0.5 c8:0.5 bb7:0.5 c8:0.5 bb7:0.5 c8:1 bb7:1 g7:1 f7:0 x:1):susT0.4,time0.5,out20,sus0.2,amp1,len8,tot7.00

    (e8:0.5 e8:1 e8:0.5 e8:0 x:2):amp1,time0.5,out20,susT0.4,sus0.2,len4.0,tot2.00

    (x:2 c6:1 g6:1 f6:1 e6:1 f6:0.5 e6:1 c6:2.5 c6:1 g6:1 f6:1 e6:1 f6:0.5 e6:1 f6:0 x:0.5 \
    ):0.5,sus0.2,out20,amp1,susT0.4,len16,tot15.50

    c8:0.25,amp0.2,pan-0.2

    c5:0.25,amp0.4,pan-0.3

#@organReed

@aPad:reed out30

    €clamp bus30,under1900,over80

    (c6:0,sus2 c5:1 e5:2 c5:1 f5:1 e5:1 . c5:2 c6:0,sus2 a4:1 c5:2 a4:1 e5:1 d5:1 c5:1 d5:0 x:1 \
        ):0.5,susT0.25,amp1,sus0.25,len16,tot15.00,pan0.1

    (bb6:1 c7:2 f6:2 c6:2 g6:4 bb6:1 g6:2 f6:1 e6:1 f6:1 c7:2 e6:2 f6:2 bb6:2 a6:3.5 c6:0 x:3.5 \
        ):sus1,susT0.5,amp1,time0.5,len32,tot28.50,pan0.15

@eBass:bass out60
    €clamp bus60,under800,over80

    (c4:4 c4:4 bb3:4 a3:2 bb3:2):chorus0.4,susT1.1,amp1,time0.5,sus4,len4.0,tot0.00,cutoff200,pan0.2

@blip:rails
    (c6:1 c7:1 bb6:1 g6:1 a6:1 c6:3 f6:1 bb6:1 f6:1 g6:0.5 a6:0.5 g6:1 \
        f6:1 c6:2 c7:1 bb6:1 g6:1 f6:1 g6:1 c6:3 f6:1 g6:3 a6:1 g6:1 f6:0 x:2 \
        ):0.5,susT2,amp1,sus0.2,len32,tot30.00,pan0.05

@karp

@arpy

@prophet

@SP_youtube
    # Example of reversing - tricky with start but it seems to accept a very high number
    #1:8,rate-0.5,start9999999999999,out20,amp0.2


@SP_Roland808:drum ofs0,sus10,amp1,bus80

    #€reverb bus80,room0.7,mix0.2,mul0.2
    €clamp bus80,under8500,over40
    €moogBass freq440,amp0,susT4,out80

    (14:1.5 14:0.5 95:1 14:1 14:1.5 14:0.5 95:2 14:1.5 14:0.5 95:1 14:1 14:1.5 14:0.5 95:0.5 14:0.5 95:0 x:1)
    (x:1 x:2 x:0.5 98:1.5 98:0 x:3)
    (26:1 26:2 26:1 26:0 x:0)
    (x:31 34:1):amp1.2,rate0.5,bus10

@SP_EMU_EDrum

@SP_EMU_SP12 ofs0,sus10,amp1,bus10,out10

    €clamp bus10,under1200,over780

    <boom> (x:31 28:1):rate0.2
    <drum> (x:12 x:1 4:0.5 4:0.5 4*2:0.5 4:0 x:1):rate2

@SP_Clavia

@SP_EMU_Proteus

@SP_Acetone

@SP_Yamaha_Grand

@SP_GBA


###########################################################################################


"""

parser = Parser()
parser.arg_defaults = {"time": Decimal("0.5"), "sus": Decimal("0.2"), "amp": Decimal("1.0")}

billboard = billboarding.parse_track_billboard(billboard, parser)
tracks = billboard.tracks
keys_config_packets = billboarding.create_keys_config_packets(billboard)

# legacy has the added function of being sent first (routers must be sent before other effects)
legacy_effects = billboarding.parse_drone_billboard(effect_billboard, parser)
print(legacy_effects)
effects = billboard.effects 
print("\n\n")
print(effects)

def configure():

    one_shot_messages = []

    client = my_client.get_default()

    client.send(jdw_osc_utils.create_msg("/set_bpm", [116]))

    # TODO: specific path read function would make things leaner and more direct 
    for sample in sample_reading.read_sample_packs("~/sample_packs"):
        client.send(jdw_osc_utils.create_msg("/load_sample", sample.as_args()))

    for synthdef in default_synthdefs.get():
        # TODO: Double check that the NRT synthdef array is not duplcicated iwth repeat calls 
        client.send(jdw_osc_utils.create_msg("/create_synthdef", [synthdef]))

    time.sleep(0.5)

    for oneshot in billboarding.create_effect_recreate_packets(legacy_effects, "fx_old_"):
        client.send(oneshot)

    for oneshot in billboarding.create_effect_recreate_packets(effects):
        client.send(oneshot)

    for oneshot in keys_config_packets:
        client.send(oneshot)


def run():
    client = my_client.get_default()


    """
    
        ISSUES & FEATURES

        - BUG: First parts of alternations don't inherit their args properly 
            - Shuttle notation issue, example: (a (b / c)):amp4 <-- b does not get amp4
            - Update: Added a test in which at least suffix reading seems ok, see "g2 = section_parsing" 
                (a (1 / 0) b)c would give "c" to 1's history, at least 

        - Synths
            - generally just expanding the library with better stuff

        - Full billboarding support
            - Bonus: "replace this track with this if running other group" 

        - Keyboard 
            - Separate key backend parts of keys and use it to revive input_lab
            - Implement all different config messages  
            - TODO: Dot-in-string-on-loop-start

        - Delay Unification
            - Since Supercollider has an internal delay, it is impossible for jackdaw apps to know <exactly> when
                a note is played for the human ear. 
            - The only way to get anywhere near this is to emit some form of event in jdw_sc to the router when 
                a note <actually> plays, either going via supercollider callback or as a delay-send to router

        - CPU Usage
            - input_lab sits at a constant 33% and makes the fans run 
            - Sequencer eats a decent amount of CPU even when stopped
                -> Ideally it should have some kind of dead-poll that is a lot slower than the current 4ms             

        - Meta-sequencer as a new app
            - Longer notes in e.g. dev-diary, but this solves many composition issues wihtout 
                making the regular sequencer more complex 

        - A return to Timeline Scores 
            ?? To better help construct longer compositions
            - STEPS:
                1. Brainstorm how and if the Tracker can be used to build longer sequences
                    - Remember the old idea of first defining a sequence and then playing
                    - So tracks can be defined as they are today, but then extended 
                    - You can easily create a separate set of collections inside the Tracker for the Scoring purpose, 
                        so that existing functionality is not affected
                    - tracks.score_into_bundles() ... 
                    - repeat_until(len) is once again essential, so that you can say "play these tracks until x time"
                        - This also allows padding with silence to keep tracks an equal length


                    - .break(name, parse, peers) can be a way of saying "play this once, creating a track for it at this time, with peers playing along"
            - Would the meta-sequencer be able to perhaps record or simplify this? To avoid reinventing the wheel? 

        - Documentation and other Boring Stuff
            - shuttle notation (once we're happy with the syntax)
            - sequencer lib (no blocker)
            - jdw sc error proofing
            - sequencer and sc OSC-driven-configuration
    
    """

    for packet in billboarding.create_effect_mod_packets(legacy_effects, "fx_old_"):
        client.send(packet)
    
    for packet in billboarding.create_effect_mod_packets(effects) + keys_config_packets:
        client.send(packet)

    queue_bundle = billboarding.create_sequencer_queue_bundle(tracks, True)

    client.send(queue_bundle)

    # Graceful ending  
    #client.send_message("/wipe_on_finish", [])
