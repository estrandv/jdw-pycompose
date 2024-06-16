from pythonosc.osc_packet import OscPacket
import time
from decimal import Decimal

import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils
from jdw_tracking_utils import Tracker, create_notes
from shuttle_notation import Parser, ResolvedElement
import sample_reading
import default_synthdefs

import client as my_client
import configure_keyboard

import billboarding

# NOTE EFFECT CHAIN QUIRK! Out bus must refer to an inbus already mentioned.
# Something something creation order of synths 
effect_billboard = """
@reverb
revone:inBus4,outBus12,mix0.15,room0.8,mul6,damp0.8,add0.02

orevtwooooo:inBus5,outBus0,mix0.35,room0.6,mul0.8,damp0.8,add0.02
@brute
#drone:amp0.2,freq440,bus4

@lowpass
masterlpf:in22,out0,freq1200,mul2
reedpassl:in76,out0,freq520,mul2
basspassl:in80,out0,freq260,mul2
brutepassl:in94,out4,freq2900

@highpass
masterhpf:in12,out22,freq40,mul1
brutepassh:in43,out94,freq900,mul1
reedpassh:in77,out76,freq270,mul2
padpassh:in111,out0,freq2500

@reverb
revthree:inBus15,outBus43,mix0.5,room0.2,mul5,damp0.8,add0.02
distverb:inBus25,outBus0,mix0.05,room0.9,mul0.18

@clamp
clampenstein:in23,out25,over270,under4400

@distortion
dister:in20,out23,drive0.65

"""

keyboard_config = """

#@synth pluck:amp0.8,susT1.5,relT0.4,bus4
#@synth distortedGuitar:amp0.1,rel5,out4,gain233
#@synth strings:amp0.5,rel2
#@synth organReed:amp1
#@synth brute:amp0.8,susT1.5,relT0.4,bus44
@synth organReed:amp0.8,susT1.5,relT0.4,out20,pan0.1
#@synth pycompose:amp1,cutoff200,susT0.1,relT0.4
#@synth gentle:amp1,susT0.1,relT0.4
#@synth feedbackPad:amp0.2,out111

"""

billboard = """

### Billboard quirks
# Tracks are named based on their line index and should not be moved around after being defined

### Billboard symbols 
# '@' denotes 'use this synth for below lines'
# '#' denotes comment line
# '<myGroup>' as first text adds the track to group 'myGroup'
# '>>>1 2 fish' defines which groups should be included (others behave as if commented)

### Note symbols 
# '§' denotes loop start time for keyboard
# 'x' denotes an empty message; silence
# '.' is ignored by the parser
# '$' denotes droning; the note will be set to on with no automated off call 
# '@' denotes modding an existing note with the suffix as id


>>> drum
>>> drum break bass
>>> drum break bass reed
>>> drum break bass riff s clap
>>> drum break bass reed chug
>>> drum break solo
>>> drum break bass reed chug clap
>>> bass break riff s
>>> drum break bass reed clap
>>> end~

@FMRhodes
<riff> (c8:0.5,sus0.25 f7:0.5,sus0.5 ab7:1,sus0.5 g7:0.5,sus0.25 ab7:0.5,sus0.5 g7:1,sus0.25 ab7:1,sus0.5 ab7:0.5,sus0.5 g7:0.5,sus0.25 ab7:0.5,sus0.25 f7:0.5,sus0.25 ab7:1,sus0.5 (g7 / eb7):0,sus0.5 x:8):sus0.2,susT1.5,relT0.4,out43,time0.5,amp0.8,len8,tot8.00,pan0.2
<solo> (c4:0,sus8 c7:1,sus1 bb6:0.5,sus0.75 g6:0.75,sus1 bb6:0.5,sus0.75 g6:0.5,sus0.75 c7:1,sus1 c6:0.5,sus0.75 c7:0.5,sus2 c6:0.75,sus1.75 bb6:0.5,sus0 bb6:0.25,sus0.5 g6:0.5,sus1 bb6:0.5,sus0.75 eb6:1,sus1.25 g6:0.5,sus0.75 eb6:1,sus1 f6:0.5,sus1.25 eb6:0.5,sus0 eb6:1.25,sus1.25 f6:1,sus1.25 eb6:0.5,sus0.5 f6:1,sus1 bb6:1,sus1 c7:0,sus1 f6:1,sus1 bb6:0.5,sus0.75 f6:1,sus1.25 g6:0.75,sus1 c7:1,sus1.25 ab6:0.5,sus0.5 g6:0.5,sus0.75 ab6:0.75,sus0.75 f6:2,sus2 c7:0,sus1.25 c6:1,sus7.5 bb6:0.5,sus0.75 g6:0.5,sus0.5 bb6:0.5,sus0.5 g6:0.5,sus0.75 f6:1,sus1 g6:3.75,sus4 c7:1,sus1 bb6:0.5,sus0.75 g6:1,sus1.25 f6:0.75,sus0.75 g6:0.75,sus1 f6:0.75,sus1 eb6:3.25,sus3.25 c6:0,sus1.25 g6:1,sus1 bb6:0.5,sus0.75 g6:0.5,sus0.75 c7:0.5,sus0.5 g6:0.5,sus0.75 c6:0,sus1.25 bb6:1,sus1 g6:1,sus1 bb6:0.5,sus0.5 f6:0.75,sus1 eb6:0.5,sus0.75 f6:0.5,sus0.5 eb6:0.5,sus0.5 c7:0,sus1.25 c6:1,sus1.25 bb6:0.5,sus0.5 g6:1,sus1 f6:1,sus1 g6:1.25,sus1.25 c6:0,sus1.75 f6:0,sus2 c7:1,sus1.25 g6:0.5,sus1 bb6:0.5,sus0.25 bb6:0.75,sus1 g6:0.75,sus1 eb6:1,sus1.25 g6:0.5,sus0.75 f6:1,sus1 g6:0.5,sus0.75 f6:1,sus1.25 c7:0.5,sus0.5 g6:1,sus1 bb6:0.5,sus0.5 g6:1,sus13.25 c6:0,sus12.25 x:1.25):relT0.4,sus0.2,pan0.1,time0.5,susT1.5,amp0.8,out20,len64,tot62.75,rel0.8
@pluck
<chug> (g6:0.25,sus0.5 g6:0.5 g6:0.25,sus0.25 g6:0.5,sus0.25 g6:0.25,sus0.25 g6:0.5,sus0.25 g6:0.25,sus0.25 g6:0.5,sus0.25 eb6:0.5,sus0.25 eb6:0.5,sus0.25 g6:0.25,sus0.25 g6:0.5,sus0.25 g6:0.25,sus0.25 g6:0.5,sus0.25 g6:0.25,sus0.25 g6:0.5,sus0.25 g6:0.25,sus0.25 g6:0.5,sus0.25 ab6:0.5,sus0.25 ab6:0,sus0.25 x:0.5):time0.5,sus0.2,relT0.4,susT1.5,amp0.8,bus15,len8,tot7.50

@brute

@strings
<s> (c6:4.25,sus1.25 f6:2,sus1.25 eb6:2,sus1 c6:0,sus2 x:7.75 x:16):amp0.05,rel2,time0.5,len16,tot8.25

@organReed
<reed> (g6:4 c6:4 g6:2 c6:2 (eb6:2 f6:0) x:2 g6:4 c6:4 g6:2 c6:2 (f6:2 eb6:0) x:2):time0.5,sus1.5,amp0.7,len16,tot14.00,rel2,out77
<reed> (c5:4 eb5:4):time0.5,sus3,amp1,len4.0,tot4.00,out77
<solo> (c6:32):sus12,amp1,len4.0,tot4.00,out77,rel8

@pycompose
#
<bass> (c4:0.75,sus0.25 g4:0.75,sus0.25 eb4:1,sus0.25 c4:0.5,sus0.25 eb4:0.5,sus0.25 c4:0.5,sus0.25 ab3:0.75,sus0.25 ab3:0.75,sus0.25 ab3:0,sus0.25 x:2.5 c4:0.75,sus0.25 g4:0.75,sus0.25 eb4:1,sus0.25 c4:0.5,sus0.25 eb4:0.5,sus0.5 c4:0.5,sus0.25 g4:0.75,sus0.25 g4:0.75,sus0.25 ab4:0.5,sus0.25 g4:1,sus0.25 eb4:0,sus0.25 x:1):time0.5,cutoff200,susT0.05,relT0.4,amp1.24,len8,tot5.50,bus80
@SP_Roland808
 #<m> (27:1 27:1 27:1 54:1):1,ofs0,amp0.5
@feedbackPad1
@gentle
@SP_EMU_EDrum
<drum> (33:0.75 33:0.25 26:0.5 33:0.5 33:0.5 x:0.5 26:0 (x:1 / x:0.25 26:0.25 27:0.5)):amp1,cutoff200,susT1.5,time0.5,sus0.2,relT0.4,len4.0,tot3.00,ofs0,bus5
<clap> (x:1 (30):3):time0.5,sus0.2,amp0.7,susT1.5,relT0.4,bus4,len4.0,tot0.00
<break> x:31 (25:0.25 25:0.25 25:0.5):time0.5,amp2,sus0.2,len4.0,tot0.50,bus4
"""

parser = Parser()
parser.arg_defaults = {"time": Decimal("0.5"), "sus": Decimal("0.2"), "amp": Decimal("0.5")}

tracks = billboarding.parse_track_billboard(billboard, parser)
konfig = billboarding.parse_keyboard_config(keyboard_config, parser)
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

        - Synths
            - gate streamlining for existing
            - generally just expanding the library with better stuff

        - Full billboarding support
            - Bonus: "replace this track with this if running other group" 
            - Bonus: "\" as line breaker

        - Keyboard 
            - Separate key backend parts of keys and use it to revive input_lab
            - Implement all different config messages  

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
