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

one_shot_messages = [
        jdw_osc_utils.create_msg("/free_notes", ["(.*)_effect(.*)"]),
        jdw_osc_utils.create_msg("/free_notes", ["bdr"]),
        jdw_osc_utils.create_msg("/note_on", ["reverb", "reverb_effect_2", 0, "inBus", 5.0, "outBus", 0.0, "mix", 0.44, "room", 0.64]),
        # Control bus example 
        jdw_osc_utils.create_msg("/c_set", [2, -114.0])

    ]

def configure():

    client = my_client.get_default()

    client.send(jdw_osc_utils.create_msg("/set_bpm", [116]))

    # TODO: specific path read function would make things leaner and more direct 
    for sample in sample_reading.read_sample_packs("~/sample_packs"):
        client.send(jdw_osc_utils.create_msg("/load_sample", sample.as_args()))

    for synthdef in default_synthdefs.get():
        # TODO: Double check that the NRT synthdef array is not duplcicated iwth repeat calls 
        client.send(jdw_osc_utils.create_msg("/create_synthdef", [synthdef]))

    time.sleep(0.5)

    for oneshot in one_shot_messages:
        client.send(oneshot)

def run():
    client = my_client.get_default()

    tracks = Tracker() 
    tracks.parser.arg_defaults = {"time": Decimal("0.5"), "sus": Decimal("0.2"), "amp": Decimal("0.5")}

    # Low cutoff pycompose is good bass! 
    configure_keyboard.as_synth(2, "pycompose", args=["amp", 1.5, "att", 0.2, "relT", 0.1, "fxa", 22.4, "cutoff", 200.0])

    # TODO: Somewhat working, albeit a bit hacky (see redundant args)
    effect_parser = Parser() 
    cur_effect = ""
    for line in effect_board.split("\n"):
        data = line.strip().split("#")[0]
        if data != "":
            if data[0] == "@":
                cur_effect = "".join(data[1:])
            elif cur_effect != "":
                element: ResolvedElement = effect_parser.parse(data)[0]
                print(element)
                note = create_notes([element], cur_effect)[0]
                one_shot_messages.append(note)

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

    @FMRhodes
    @pluck
    @brute
    @pycompose
    @SP_Roland808
    # <m> (27:1 27:1 27:1 54:1):1,ofs0,amp0.5
    @feedbackPad1
    @gentle

    """

    line_filter = "" # Populated with ">>>" 
    line_index = 0
    synth = "pycompose" # Default value 
    for line in billboard.split("\n"):

        data = line.strip()

        if data != "":

            # Consume group symbol, if existing
            group_symbol = ""
            if len(data) > 2 and data[0] == "<" and data[2] == ">":
                group_symbol = data[1]
                print("Group detected!", group_symbol)
                data = "".join(data[3:])

            group_pass = group_symbol == "" or line_filter == "" or group_symbol in line_filter

            # Group filter definition

            is_filter_definition = len(data) > 3 and "".join(data[0:3]) == ">>>"

            if is_filter_definition:
                line_filter = "".join(data[3:])
                print("Group filter detected!", line_filter)

            if not is_filter_definition:

                # Increase even for ignored tracks, to avoid renaming tracks on uncomment
                line_index += 1

                if group_pass:

                    if data[0] == "@":
                        synth = "".join(data[1:])
                        line_index = 0
                    elif data[0] != "#":

                        name = "chunk_track_" + synth + "_" + str(line_index)
                        tracks[name + ":" + synth] = data

        """
    
        ISSUES & FEATURES

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


    # Sequencer queue 
    client.send(tracks.into_sequencer_queue_bundle())

    # NRT Record 
    for bundle in tracks.into_nrt_record_bundles(one_shot_messages):
        #client.send(bundle)
        pass 


    # Graceful ending  
    #client.send_message("/wipe_on_finish", [])
