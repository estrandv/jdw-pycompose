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

"""
BILLBOARD REVIEW, SO FAR
- Update doesn't always hit. Could be that the sleep timing is wrong,
    could be some missing order part. 
- Slightly annoying that new effects need complete reset while 
    existing ones can just be tweaked live. 
    * One way around it is existing effects, but that's hard to prep. 
- Keeping track of bus chains is a chore
    * ReplaceOut would at least limit us to one bus per track
        - Order becomes important, but I think that's ok 
        - Chaining still possible, but we will need separate definitions for 
            many different tracks
- Need plenty more synths and effects
    - and streamlining ... 
- bus-as-arg can be a bit of a pain to track
    * default or override args should be provided in meta-data 
        - Default is enough for bus and a good start
        - Override is harder and hackier but would ultimately be good for transpose
            - ... but since octave is not really an arg I think we're fine
            - ... octave is just iter().upIndex().collect() before osc conversion 

There are more issues, but the above should give a good headstart 







"""




# NOTE EFFECT CHAIN QUIRK! Out bus must refer to an inbus already mentioned.
# Something something creation order of synths 
effect_billboard = """

@reverb
barrb:inBus32,outBus0,mix0.65,room0.8,mul2

@distortion

"""

keyboard_config = """

@synth pluck:amp0.8,susT0.1,relT0.4,bus4
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

### Billboard quirks
# Tracks are named based on their line index and should not be moved around after being defined

### Billboard symbols 
# '@' denotes 'use this synth for below lines'
# '#' denotes comment line
# '<myGroup>' as first text adds the track to group 'myGroup'
# '>>>1 2 fish' defines which groups should be included (others behave as if commented)
# 'backslash' COMBINES LINES natively in python

### Note symbols 
# '§' denotes loop start time for keyboard
# 'x' denotes an empty message; silence
# '.' is ignored by the parser
# '$' denotes droning; the note will be set to on with no automated off call 
# '@' denotes modding an existing note with the suffix as id

#>>> end

@FMRhodes
@pluck
@brute
@strings
@organReed
@pycompose
@SP_Roland808
@feedbackPad1
@gentle
@SP_EMU_EDrum
<drum> (34:0.5 34:0.5 33:0.5 34:0.25 33:0.75 35:0.5 33:0 x:1):sus0.2,amp0.8,time0.5,susT0.1,relT0.4,bus4,len4.0,tot3.00,bus4,ofs0
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
