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

# 30 
@delay masterdel:bus30,echo0.125,echt8
@clamp camper:bus30,over400,under8000,mul0.45

# 40 - dist
@reverb vahaa:bus40,mix0.65,room0.6,mul2
@clamp clampstamp:bus40,under6700,over500,mul0.11
@distortion masterdistt:bus40,drive0.3

# 20
@reverb drumverb:bus20,mix0.35,room0.5,mul1.2
@clamp ohclamp:bus20,under620,over480,mul1.1

# 50 - bass
@clamp clampp:bus50,under250,over80,mul0.8

# 60
@reverb asda:bus60,mix0.75,room0.8,mul1
@clamp toneitdown:bus60,under1800,over380,mul0.4
@delay WIZ:bus60,echo0.100007,echt8.5

# 70 - blip
@clamp clasblippampp:bus70,under7150,over280,mul0.5

# 80
@reverb reedify:bus80,mix0.75,room0.8,mul2
@clamp reeed:bus80,under1150,over180,mul0.5

# 90 - soundclips
@reverb youtube:bus90,mix0.55,room0.9,mul4
@clamp tclamp:bus90,under7350,over180,mul0.55

"""

keyboard_config = """

#################
# K E Y B O A R D [¤]
#################

# Standin until pad args are configured separately
@synth blip:ofs0,amp0.2,bus20,sus10,susT10

#@synth eBass:amp1,cutoff200,susT0.1,relT0.1
#@synth prophet:amp0.2,susT0.5


#@synth blip:amp1,rate2

#@synth pluck:amp0.8,susT0.1,relT0.4,bus4
#@synth karp:amp0.8,susT0.5,relT0.5
#@synth distortedGuitar:amp0.1,rel5,out4,gain233
#@synth strings:amp0.5,rel2
#@synth K:amp1
#@synth brute:amp0.1,susT1.5,relT0.4,bus30
#@synth K:amp0.8,susT1.5,relT0.4,pan0.1
#@synth FMRhodes:amp0.4,susT0.1,relT0.4
#@synth feedbackPad:amp0.2,out111

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

>>> bass
>>> bass between
>>> bdrum hdrum bass between
>>> bdrum hdrum bass dist
>>> bdrum hdrum bass bus_short reed
>>> bdrum hdrum bass between dist
>>> bdrum hdrum bass dist cele rdrum
>>> bdrum hdrum bass reed sitar tubes
>>> bdrum hdrum bass reed between cdrum
>>> dist rdrum cele reed tubes
>>> dist cele cdrum bus sitar
>>> bass bdrum hdrum rdrum between reed
>>> bdrum hdrum bass reed ramp dist
>>> end

#>>> bdrum hdrum bass reed


#>>> end

@prophet

@blip
<ramp;out70> (eb6:0.5,sus0.25 c6:0.5,sus0.25 g6:1,sus0.25 eb6:1,sus0.25 ab6:1,sus0.25 g6:0.5,sus0.25 eb6:1,sus0.25 c6:2.5,sus0.25 eb6:0.5,sus0.25 c6:0.5,sus0.25 eb6:1,sus0.25 g6:1,sus0.25 bb6:0.5,sus0.25 ab6:1,sus0.25 g6:1,sus0.25 f6:0.5,sus0.25 eb6:2,sus0.25 c6:0.5,sus0.25 eb6:1,sus0.25 f6:0.5,sus0.25 g6:1,sus0.25 f6:0.5,sus0.25 eb6:1,sus0.25 c6:1,sus0.25 c6:1,sus0.25 eb6:1.5,sus0.25 c6:0.5,sus0.25 eb6:1,sus0.25 f6:0.5,sus0.25 g6:2,sus0.25 bb6:0.5,sus0.25 g6:1,sus0.25 f6:1,sus0.25 g6:0.5,sus0.25 ab6:1,sus0.25 eb6:0,sus0.25 x:0):rate2,time0.5,sus0.2,amp0.5,len32,tot32.00,pan-0.1
<between;out70> (g6:0.5,sus0.25 g6:1,sus0.25 g6:0.5,sus0.25 g6:1,sus0.25 eb6:0.5,sus0.25 eb6:4.5,sus0.25 g6:0.5,sus0.25 g6:1,sus0.25 g6:0.5,sus0.25 g6:1,sus0.25 ab6:0.5,sus0.25 ab6:1,sus0.25 g6:0,sus0.25 x:3.5):time0.5,amp0.8,sus0.2,rate2,len16,tot12.50,pan-0.1
<between;out70> (x:4.5,sus0.25 c7:0.5,sus0.25 c7:0.5,sus0.25 eb7:0.5,sus0.25 c7:1,sus0.25 bb6:0,sus0.25 x:9):amp0.4,sus0.2,rate2,time0.5,len8,tot7.00,pan0.15

@eBass
<bass;out50> ((c4*4:0.75 c4*2:0.5) (ab3*4:0.75 ab3*2:0.5) (g3*4:0.75 g3*2:0.5) (ab3*4:0.75 ab3*2:0.5)):cutoff200,sus0.2,susT0.1,relT0.2,time0.5,amp1,len4.0,tot3.50,pan-0.25

@FMRhodes
<dist;out40> ((c6 / eb6 / f6 / ab6):0.5,sus0.25 bb5:0.25,sus0.25 bb6:0.5,sus0.25 eb6:0.25,sus0.25 bb6:0.5,sus0.25 c7:0.5,sus0.25 bb6:0.5,sus0.25 eb6:0.5,sus0.25 bb6:0,sus0.25 x:0.5):sus0.2,relT0.4,susT0.1,amp0.4,time0.5,len4.0,tot3.50,pan0.5

@pluck

@karp
<sitar;out60,pan0.6>(eb6:3,sus0.25 f6:1,sus0.25 g6:1.5,sus0.25 eb6:2.5,sus0.25 g6:3,sus0.25 ab6:1,sus0.25 g6:1.5,sus0.25 f6:0,sus0.25 x:2.5):susT0.5,relT0.5,time0.5,sus0.2,amp0.8,len16,tot13.50

@organReed
<reed;out80> (c5:8,sus4.5 eb5:4,sus2 g4:4,sus2 c5:8,sus4.5 eb5:4,sus2 d5:4,sus2):sus0.2,amp0.8,time0.5,susT1.5,relT1,pan0.1,len32,tot28.00,pan-0.15

@eBass

@blip

@karp

@arpy
#<;out30> (c6 eb6 f6 (eb5 / g5):0 c6):2,susT2,relT4
<cele;out30> (eb8:8 eb8:4 bb7:4):2,susT2,relT4,amp0.25,pan0.5

@prophet

@SP_youtube
<tubes;bus90> 1:32,amp0.015,sus10,rate0.9,ofs0,start2000.24
<bus;bus90> 0:16,amp0.1,sus8.5,rate0.8,ofs0,start20000
<bus_short;bus90> 0:32,amp0.05,sus3,rate0.8,ofs0.1,start20000

@SP_Roland808

@SP_EMU_EDrum
<hdrum;bus20> ((x:0.75 11:0.75 x:1 33:0.5 11:0 x:1)*3 (11:0.25 50:0.5 50:0.5 11:0 x:1.75 53:1,amp*0.5)):amp0.2,sus10,ofs0,time0.5,len4.0,tot3.00
<bdrum;bus20> (5:1.5 5:0.5 5:0 x:2):bus10,sus0.2,amp0.3,ofs0.0,time0.5,len4.0,tot2.00,rate1
<rdrum;bus20> (57:0.25 57:0.25 57:0 x:3.5 x:12):ofs0,bus20,amp0.05,time0.5,sus10,susT10,len4.0,tot0.25,pan0.3
<cdrum;bus20> (x:15 53*2:0.5):susT10,time0.5,sus10,ofs0,amp0.05,bus20,len4.0,tot0.00,pan0.4




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
