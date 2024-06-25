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

# drum
#@reverb dverb:bus80,room0.7,mix0.2,mul0.2
@clamp drumc:bus80,under8500,over40

# 90
@reverb coverb:bus90,room0.2,mix0.7,mul0.8
@clamp corumc:bus90,under1500,over480

# 30
@clamp reeeds:bus30,under1900,over80

# 20
@reverb corarb:bus20,room0.8,mix0.7,mul0.8
@clamp RAHARB:bus20,under1500,over880

# call
#@delay calld:bus70,echo0.125,echt4

# d bass 
@clamp mooogz:bus60,under800,over80

# 10 weird drums
@clamp AGARAR:bus10,under1200,over780

# 50 prop
@delay ROAADA:bus50,echo0.25,echt4
@reverb ROP:bus50,room0.9,mix0.9,mul0.8
@clamp ROPS:bus50,under6200,over1780



"""

# TODO: Extend keyboard configuration options for convenience
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


#>>> end

# TODO: Would be really neat if you could just slap some defaults and a marker in here and have it become the keyboard synth
# instead of having to scroll
# but of course that could be messsy, especially with the defaults 

# BEFORE NEXT SONG
# 1. Make sample pack configurable in keyboard via OSC 
# 2. Make sus-appending in keyboard toggleable 
# 3. Streamline SAMPLER to conform to new standard



# BASS DRUM COURT RIDE

>>> drum
>>> drum keys
>>> drum keys bass cele cymbal
>>> drum keys bass 
>>> drum keys bass prophet cymbal
>>> drum keys bass rails cymbal
>>> drum keys cele cymbal
>>> drum bass keys reed
>>> drum bass keys prophet reed cymbal
#>>> drum keys
#>>> drum keys bass rails cymbal
#>>> drum keys cele
#>>> keys reed prophet insanity

@prophet

@blip

@ksBass

@dBass

@moogBass
<prophet;out50> (x:1 c6:1 e6:1 f6:1 e6:0,susT2 x:12):time0.5,susT0.5,sus0.01,amp1,len8,tot8.00,lfoS2,cutoff4000

@eBass

@FMRhodes
#(c4:4):chorus0.4,susT1.1,amp1,time0.5,sus4,len4.0,tot0.00
<keys> (c5:4 c5:4 bb4:4 a4:2 bb4:2):chorus0.4,susT1.1,amp1,time0.5,sus4,len4.0,tot0.00
<cele;out20> (c6:1 bb6:1 a6:0.5 g6:1.5 f6:1 g6:0.5 a6:1 f6:0.5 g6:0 x:1):sus0.25,chorus0.5,relT0.8,amp0.4,cutoff1000,len8,tot7.00,out20

@pluck
<insanity;out20> (c7:1 c8:0.5 bb7:0.5 c8:0.5 bb7:0.5 c8:0.5 bb7:0.5 c8:1 bb7:1 g7:1 f7:0 x:1):susT0.4,time0.5,out20,sus0.2,amp1,len8,tot7.00
<insanity;out20> (e8:0.5 e8:1 e8:0.5 e8:0 x:2):amp1,time0.5,out20,susT0.4,sus0.2,len4.0,tot2.00
<insanity;out20> (x:2 c6:1 g6:1 f6:1 e6:1 f6:0.5 e6:1 c6:2.5 c6:1 g6:1 f6:1 e6:1 f6:0.5 e6:1 f6:0 x:0.5):time0.5,sus0.2,out20,amp1,susT0.4,len16,tot15.50
<insanity;out20> c8:0.25,amp0.2
<insanity;out20> c5:0.25,amp0.4

@organReed

@aPad
<reed;out30> (c6:0,sus2 c5:1 e5:2 c5:1 f5:1 e5:1 . c5:2 c6:0,sus2 a4:1 c5:2 a4:1 e5:1 d5:1 c5:1 d5:0 x:1):time0.5,susT0.25,amp1,sus0.25,len16,tot15.00
<reed;out30> (bb6:1 c7:2 f6:2 c6:2 g6:4 bb6:1 g6:2 f6:1 e6:1 f6:1 c7:2 e6:2 f6:2 bb6:2 a6:3.5 c6:0 x:3.5):sus1,susT0.5,amp1,time0.5,len32,tot28.50


@eBass
<bass> (c4:4 c4:4 bb3:4 a3:2 bb3:2):chorus0.4,susT1.1,amp1,time0.5,sus4,len4.0,tot0.00,cutoff200

@blip
<rails> (c6:1 c7:1 bb6:1 g6:1 a6:1 c6:3 f6:1 bb6:1 f6:1 g6:0.5 a6:0.5 g6:1 f6:1 c6:2 c7:1 bb6:1 g6:1 f6:1 g6:1 c6:3 f6:1 g6:3 a6:1 g6:1 f6:0 x:2):time0.5,susT2,amp1,sus0.2,len32,tot30.00

@karp

@arpy

@prophet

@SP_youtube

@SP_Roland808
<drum;bus80> (14:1.5 14:0.5 95:1 14:1 14:1.5 14:0.5 95:2 14:1.5 14:0.5 95:1 14:1 14:1.5 14:0.5 95:0.5 14:0.5 95:0 x:1):ofs0,amp1,sus10
<drum;bus80> (98:2 98:1 98:0.5 98:1.5 98:0 x:3):ofs0,amp1,sus10
<drum;bus80> (26:1 26:2 26:1 26:0 x:0):ofs0,amp1,sus10
<cymbal> (x:31 34:1):ofs0,amp1,sus10,rate0.5,bus10

@SP_EMU_EDrum

@SP_EMU_SP12
(x:31 28:1):ofs0,sus10,amp1,bus10,rate0.2
(x:12 x:1 4:0.5 4:0.5 4*2:0.5 4:0 x:1):ofs0,sus10,amp1,bus10,rate2

@SP_Clavia

@SP_EMU_Proteus

@SP_Acetone

@SP_Yamaha_Grand

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
