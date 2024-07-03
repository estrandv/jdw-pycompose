# Sets up some sane defaults (routers, synths, samples) and then runs a .bbd file as described


from pythonosc.osc_packet import OscPacket
import time
from decimal import Decimal

import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils
from shuttle_notation import Parser, ResolvedElement
import sample_reading
import default_synthdefs

import client as my_client

import billboarding
import traceback

import os


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
            -> As in "gain the external id" so that you can switch things mid play for shorter tracks

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
        - Syntax? 
            >>> drum bass riff §4
            >>> drum bass chords §2
            ... doesn't have to be harder 

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
            - You have all the notes available at the start, but you might not want to read them too carefully?
            - You can technically reverse things the same way that the keyboard does, plus individual args. 
                -> You'd get pretty messed up code, but it would work
                -> Still, you can do this just fine in jdw-pycompose without involving another application 

        

    - Documentation and other Boring Stuff
        - shuttle notation (once we're happy with the syntax)
        - sequencer lib (no blocker)
        - jdw sc error proofing
        - sequencer and sc OSC-driven-configuration

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

@router routerrails:ofs0,sus10,amp1,bus80,in80,out0

@router tnin:in90,out0

"""

def read_bdd(bdd_name: str) -> billboarding.BillBoard:
    parser = Parser()
    parser.arg_defaults = {"time": Decimal("0.5"), "sus": Decimal("0.2"), "amp": Decimal("1.0")}

    path = os.path.dirname(os.path.realpath(__file__))
    content = open(path + "/" + bdd_name, 'r').read().replace("\\\n", "")
    return billboarding.parse_track_billboard(content, parser)

def error_beep():
    for i in [190.0, 300.0]:
        beep = jdw_osc_utils.create_msg("/note_on_timed", ["default", "error_beep", "0.1", 0, "freq", i, "amp", 1.0])
        my_client.get_default().send(beep)

def configure(bdd_name: str):
    try:

        billboard = read_bdd(bdd_name)
        keys_config_packets = billboarding.create_keys_config_packets(billboard)
        # legacy has the added function of being sent first (routers must be sent before other effects)
        legacy_effects = billboarding.parse_drone_billboard(effect_billboard, Parser())

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

        for oneshot in billboarding.create_effect_recreate_packets(billboard.effects):
            client.send(oneshot)

        for oneshot in keys_config_packets:
            client.send(oneshot)
    except Exception as e:
        print(traceback.format_exc())
        error_beep() 

def run(bdd_name: str):

    client = my_client.get_default()

    try: 

        billboard = read_bdd(bdd_name)
        keys_config_packets = billboarding.create_keys_config_packets(billboard)

        # TODO: Include in billboard somehow 
        keys_config_packets.append(jdw_osc_utils.create_msg("/keyboard_quantization", ["0.25"]))

        # legacy has the added function of being sent first (routers must be sent before other effects)
        legacy_effects = billboarding.parse_drone_billboard(effect_billboard, Parser())

        for packet in billboarding.create_effect_mod_packets(legacy_effects, "fx_old_"):
            client.send(packet)

        for packet in billboarding.create_effect_mod_packets(billboard.effects) + keys_config_packets:
            client.send(packet)

        queue_bundle = billboarding.create_sequencer_queue_bundle(billboard.tracks, True)

        client.send(queue_bundle)
    except Exception as e:
        print(traceback.format_exc())
        error_beep() 

    # Useful in the past, not as important now with batch sending
    #client.send_message("/wipe_on_finish", [])
