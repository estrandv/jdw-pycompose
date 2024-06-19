from pythonosc.osc_packet import OscPacket
import time
from decimal import Decimal

import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils
from shuttle_notation import Parser, ResolvedElement
import sample_reading
import default_synthdefs

import client as my_client
import configure_keyboard

import billboarding


"""

# Billboard Cheat Sheet (tracks)

### Billboard quirks
# Tracks are named based on their line index and should not be moved around after being defined

### Billboard symbols 
# '@' denotes 'use this synth for below lines'
# '#' denotes comment line
# '<...>' as first text denotes meta-data (see separate note)
# '>>>1 2 fish' defines which groups should be included (others behave as if commented)
# 'backslash' COMBINES LINES natively in python

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

###############
# E F F E C T S ><
###############

# Routers created first, so as to appear last
@router tone:in10,out0
@router ttwo:in20,out0
@router tthr:in30,out0
@router tfou:in40,out0
@router tfiv:in50,out0
@router tsix:in60,out0
@router tsev:in70,out0
@router teig:in80,out0
@router tnin:in90,out0

"""

# TODO: Extend keyboard configuration options for convenience
keyboard_config = """

#################
# K E Y B O A R D [¤]
#################

#@synth eBass:amp4,cutoff200,susT0.1,relT0.1
@synth prophet:amp1,susT0.5

@sampler EMU_Proteus:ofs0,sus10,amp1
@sampler EMU_EDrum:ofs0,sus10,amp1
#@sampler Roland808:ofs0,sus10,amp1
@pads 1:0 2:4 3:8 4:12 5:16 6:20 7:24 8:28

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


>>> end

# TODO: Would be really neat if you could just slap some defaults and a marker in here and have it become the keyboard synth
# instead of having to scroll
# but of course that could be messsy, especially with the defaults 

# BEFORE NEXT SONG
# 1. Make sample pack configurable in keyboard via OSC 
# 2. Make sus-appending in keyboard toggleable 
# 3. Streamline SAMPLER to conform to new standard

@prophet

@blip
(a6:0.5,sus0.25 f6:0.5,sus0.25 f6:0.5,sus0.25 g6:0.5,sus0.25 f6:0.5,sus0.25 f6:0.5,sus0.25 eb6:0.5,sus0.5 f6:0.5,sus0.5 eb6:0.5,sus0.5 f6:0.5,sus0.25 g6:0,sus0.25 x:3):ofs0,susT10,bus20,sus10,amp0.2,time0.5,len8,tot5.00

@ksBass

@dBass

@moogBass

@eBass

@FMRhodes

@pluck

@organReed


@eBass

@blip

@karp
@arpy

@prophet

@SP_youtube
1:32,amp0.1,sus20,rate0.5

@SP_Roland808

@SP_EMU_EDrum
29:4,ofs0,sus4
(x:2 23:0.5 23:0.5 23:0.5 23:0 x:4.5):time0.5,amp0.2,bus20,susT10,sus10,ofs0,len4.0,tot1.50

@SP_EMU_SP12
((31 32)*3 (31 32*2:0.25 33:0.5)):1,ofs0

@SP_Clavia
#(30 1 2 3 4 5 6 7):ofs0,amp0.2,sus10

@SP_EMU_Proteus
#(0 1 2 13 4 5 6 7):ofs0,amp0.2,sus10

@SP_Acetone
(0 1 2 13 4 5 6 7):ofs0,amp0.2,sus10

@SP_Yamaha_Grand
(24 24:rate0.22):4,ofs0,amp0.2,rate0.2,sus10

@SP_GBA



###########################################################################################


"""

parser = Parser()
parser.arg_defaults = {"time": Decimal("0.5"), "sus": Decimal("0.2"), "amp": Decimal("1.0")}

tracks = billboarding.parse_track_billboard(billboard, parser)
konfig = billboarding.parse_oneline_configs(keyboard_config, parser)
effects = billboarding.parse_drone_billboard(effect_billboard, parser)

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

    one_shot_messages += billboarding.create_effect_recreate_packets(effects)
    one_shot_messages += billboarding.create_keyboard_config_packets(konfig)

    for oneshot in one_shot_messages:
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

    for packet in billboarding.create_effect_mod_packets(effects) + billboarding.create_keyboard_config_packets(konfig):
        client.send(packet)

    queue_bundle = billboarding.create_sequencer_queue_bundle(tracks, True)

    client.send(queue_bundle)

    # Graceful ending  
    #client.send_message("/wipe_on_finish", [])
