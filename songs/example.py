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
@router drumrouter:in20,out0
@router flatout:in30,out0
@router other:in32,out0

# 30 
@delay masterdel:bus30,echo0.125,echt8
@clamp masterclamp:bus30,under800,over40,mul0.3
@distortion masterdist:bus30,drive0.8

# 32
@distortion masterdistt:bus32,drive0.3
@clamp clampstamp:bus32,under1800,over400,mul0.5
@delay plclam:bus32,echo0.25,echt2

# 6 drum
@reverb drumverb:bus20,mix0.75,room0.8,mul4


"""

keyboard_config = """

#################
# K E Y B O A R D [¤]
#################

# Standin until pad args are configured separately
@synth blip:ofs0,amp1,bus20

#@synth pluck:amp0.8,susT0.1,relT0.4,bus4
#@synth distortedGuitar:amp0.1,rel5,out4,gain233
#@synth strings:amp0.5,rel2
#@synth organReed:amp1
#@synth brute:amp0.1,susT1.5,relT0.4,bus30
#@synth organReed:amp0.8,susT1.5,relT0.4,out20,pan0.1
#@synth pycompose:amp1,cutoff200,susT0.1,relT0.1
#@synth FMRhodes:amp0.4,susT0.1,relT0.4,out30
#@synth feedbackPad:amp0.2,out111

"""

billboard = """

#############
# T R A C K S ¶
#############

#>>> end

@FMRhodes


@pluck

@organReed

@eBass

@blip
#(g7 a7 c7 d7):4,susT5,rate442

@karp
<;out30> (g7 g7 a7 f7 . a7 a7 a7 x . g7 d7 a7 x . f7 f7 a7 d7):1,amp0.2,susT2

@arpy
<;out32> (g7 g7 a7 f7 . a7 a7 a7 x . g7 d7 a7 x . f7 f7 a7 d7\
    ):1,amp0.4,susT2

@prophet
<;out30> (g6 a6 c6 d6):4,susT2,rate2,lforate440,amp0.4


@SP_Roland808

@SP_EMU_EDrum
<;bus20> (33:0.75 33:0.75 33:1 33:0.5 33:0 x:1):amp0.2,sus0.2,ofs0,time0.5,len4.0,tot3.00






###########################################################################################


"""

parser = Parser()
parser.arg_defaults = {"time": Decimal("0.5"), "sus": Decimal("0.2"), "amp": Decimal("0.5")}

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


    # Low cutoff pycompose is good bass! 
    #configure_keyboard.as_synth(2, "pycompose", args=["amp", 1.5, "att", 0.2, "relT", 0.1, "fxa", 22.4, "cutoff", 200.0])

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
