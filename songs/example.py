from pythonosc.osc_packet import OscPacket
import time
from decimal import Decimal

import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils
from jdw_tracking_utils import Tracker
import sample_reading
import default_synthdefs

import client as my_client
import configure_keyboard

one_shot_messages = [
        jdw_osc_utils.create_msg("/free_notes", ["(.*)_effect(.*)"]),
        jdw_osc_utils.create_msg("/free_notes", ["bdr"]),
        jdw_osc_utils.create_msg("/note_on", ["reverb", "reverb_effect_1", 0, "inBus", 4.0, "outBus", 0.0, "mix", 0.64, "room", 0.24]),
        jdw_osc_utils.create_msg("/note_on", ["reverb", "reverb_effect_2", 0, "inBus", 5.0, "outBus", 0.0, "mix", 0.94, "room", 0.34]),
        jdw_osc_utils.create_msg("/note_on", ["control", "cs", 0, "bus", 55.0, "prt", 0.5]),
        jdw_osc_utils.create_msg("/note_on", ["brute", "bdr", 0, "amp", 0.0]),
        # Control bus example 
        #jdw_osc_utils.create_msg("/c_set", [44, -4.0])

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


    # TODO: pycompose does not have a working gate setting, sadly

    # Drum presets 
    #configure_keyboard.as_sampler("EMU_EDrum") 


    # Low cutoff pycompose is good bass! 
    #configure_keyboard.as_synth(2, "pycompose", args=["amp", 1.5, "att", 0.2, "relT", 0.1, "fxa", 22.4, "cutoff", 200.0])
    
    #configure_keyboard.as_synth(4, "pycompose", args=["amp", 0.9, "att", 0.2, "relT", 0.8, "fxa", 22.4])
    configure_keyboard.as_synth(4, "pluck", args=["amp", 0.9, "att", 0.2, "relT", 0.8, "fxa", 22.4])
    #configure_keyboard.as_synth(4, "gentle", args=["amp", 0.8, "att", 0.2, "relT", 0.1, "fxa", 22.4, "cutoff", 200.0])
    #configure_keyboard.as_synth(4, "feedbackPad1", args=["amp", 0.1, "att", 0.2, "relT", 0.1, "fxa", 22.4, "cutoff", 200.0])

    #tracks["metronome:SP_Roland808"] = "(56 36 56 36 56 36 56 40):ofs0"

    billboard = """
    @brute
    a4:4
    
    """

    billboard2 = """
    
    ### Billboard symbols 
    # '@' denotes 'use this synth for below lines'
    # '#' denotes comment line
    
    ### Note symbols 
    # '§' denotes loop start time for keyboard

    @brute
(_:0.00,amp0 bb4:0.75,sus0.09974 a4:0.75,sus0.08848 g4:0.5,sus0.09547 f4:2,sus0.1101 f4:0.75,sus0.1047 g4:0.75,sus0.1175 a4:0.5,sus0.09208 bb4:0.75,sus0.09966 a4:0.75,sus0.09474 g4:0.5,sus0.1121 eb4:2,sus0.1459 c4:0.75,sus0.1205 f4:0.75,sus0.1001 g4:0.5,sus0.07715 eb4:2,sus0.1316 c4:0.75,sus0.1064 eb4:0.75,sus0.09516 g4:0.5,sus0.1309 bb4:0.75,sus0.1309 a4:0.75,sus0.1070 g4:0.5,sus0.07676 f4:2,sus0.1011 f4:0.75,sus0.09093 g4:0.75,sus0.09177 a4:0.5,sus0.1006 bb4:0.75,sus0.1021 a4:0.75,sus0.1114 g4:0.5,sus0.1056 f4:2,sus0.1022 c4:2,sus0.1208 f4:1,sus0.1008 eb4:1,sus0.1201 f4:1,sus0.1349 g4:1,sus0.1098 g4:2.25,sus0.1173 f4:1.75,sus0.1120):amp0.25,fxa22.4,att0.2,relT0.8,len36.00

    @pluck
(_:0.00,amp0 c4:1.5,sus0.09088 f4:0.5,sus0.06649 g4:0.75,sus0.09566 a4:0.75,sus0.1045 f4:0.5,sus0.07216 g4:4,sus0.07416 c4:1.5,sus0.06484 f4:0.5,sus0.06637 g4:0.75,sus0.09982 a4:0.75,sus0.08236 f4:0.5,sus0.1032 g4:2,sus0.1149 f4:2,sus0.1367):sus+1,fxa22.4,rel2.8,att0.2,amp0.9,len16
    @SP_Roland808


    @feedbackPad1
#(_:0.00,amp0 g4:4,sus1.783 bb4:1.75,sus0.7166 a4:2,sus0.6711 f4:8,sus0.6821 bb4:1.5,sus0.6621 bb4:1.5,sus0.1473 a4:1.5,sus0.4699 g4:1.5,sus0.4412 f4:2,sus0.6559 c4:0.25,sus0.1054 c4:0,sus0.4668):att0.2,fxa22.4,amp0.1,relT0.1,cutoff200,len24

    @pycompose
#(§:0 c2:0.75,sus0.09579 a2:0.75,sus0.09592 f2:0.5,sus0.08290 g2:0.75,sus0.1750 a2:0.75,sus0.09980 f2:0.5,sus0.06643 g2:0.75,sus0.09916 a2:0.75,sus0.08132 f2:0.5,sus0.08707 g2:1,sus0.09572 f2:1,sus0.08421):relT0.4,attT0.0,amp1.8,fxa22.4,cutoff200,len8

(_:0.00,amp0 c3:0.5,sus0.05391 bb2:0.75,sus0.08171 a2:0.75,sus0.06662 f2:0.75,sus0.08744 a2:0.75,sus0.06141 bb2:0.5,sus0.09421):att0.2,fxa22.4,cutoff200,relT0.1,amp1.5,len4.0
    
    @SP_EMU_EDrum
    #(20*3 4):ofs0
    (§:0 20:0.75 20:0.25 44:0.5 20:0.5 20:0.75 20:0.25 44:1):ofs0,amp1,sus0.5,relT2.5,len4
    (x:3.5,amp0 40:4.5):sus0.5,ofs0,relT2.5,amp1,len4.00
    #(x:3.25,amp0 83:0.5 83:4.25):ofs0.2,sus0.5,relT2.5,amp0.2,len4.00
    
    @gentle
(_:0.00,amp0 f4:0.5,sus0.07446 a4:0.5,sus0.06949 bb4:0.5,sus0.07103 a4:0.5,sus0.06695 bb4:0.5,sus0.05788 a4:0.25,sus0.06844 bb4:0.75,sus0.06117 (a4 / c5):0.5,sus0.07439):relT0.1,att0.2,amp0.2,fxa22.4,len4.0

(_:0.00,amp0 a3:0.5,sus0.07325 b3:0.5,sus0.08740 c4:0.5,sus0.06724 a3:2.5,sus0.05455):amp0.8,fxa22.4,att0.2,cutoff200,relT0.1,len4.0

    """

    line_index = 0
    synth = "pycompose" # Default value 
    for line in billboard.split("\n"):

        data = line.strip()

        if data != "":
            # Increase even for comments, to avoid renaming tracks on uncomment
            line_index += 1

            if data[0] == "@":
                synth = "".join(data[1:])
                line_index = 0
            elif data[0] != "#":

                name = "chunk_track_" + synth + "_" + str(line_index)
                tracks[name + ":" + synth] = data

        """
    
        YES HELLO THIS IS FEATURE PLANNING AGAIN

        - Annoying things while jamming:
            * If some tracks are very long, calling queue will stop shorter tracks until a new loop begins
                - This has something to do with wipe_on_finish, but feels a bit hard to explain
                    - wipe is called: all tracks will end when finishing
                    - queue is called: all mentioned tracks remove the wipe flag
                - Could also be the new bilboard solution causing different track names  
                    -> I think this was the case
                - ANOTHER ISSUE THOU: If a track is notably shorter than the longest, it will stop too soon
                    -> Ideally, tracks should stop when the next long loop finishes 
            * AMP arg in SAMPLER appears breakable
                - Sometimes when there are multiple sampler synths active..? 
            * Relative args should have smarter resolution
                - E.g. setting "sus+4" on top level so that one can tinker with times that got messed up by keyboard 
                    -> Math rules is one way to handle it 
                    -> Custom mod also works, of course. One can keep the shuttle rules and just
                        eat into the string to process the args after the fact 

        - Jamming with friends
            - TODAY: 
                - If one person could play while the other controls the text, it would create a neat dynamic in itself
                    - Requirements: 
                        - Non-main keyboard input device (that other person can sit with elsewhere)
                        - Universal input reading, without window focus 
                        -> Generally: Wiring up the MIDI keyboard would have a lot of good results 
                        -> Should not replace current keyboard, but be an alternative to it 
                        -> "Please save that one" is an easy way to transfer data when jamming, even if there is 
                            no way to send directly 
            - Secondary input sources 
                - For a device to be independent, it must be able to send queues to the jam without a clipboard middleman 
                    - OPTION A: Interface, with hidden sequences
                        - Requires: Tracks, Send, Wipe, 
                    - OPTION B: Auto-write to common file 
                        - Similar requirements, honestly, but could hack it as a pure print-to in beginning of course 
                        - 

        - Delay Unification
            ?? Because we should have a general idea, across applications, of when an actual sound is played 
            - Keyboard has a hard time differentiating between message arrival and play time due to SC delay
            - Also: JDW_SC still has that awkward middleman problem where most added features are just ways 
                around doing things "natively". 
            - NOTE_ON_TIMED
                - The gate_off message can be sent as part of the sequence if it is allowed to be delayed 
                - The main issue is that the sequencer does not know the contents of its messages
                    -> And so, each loop can only have the same constant time
                    -> ... while supercollider uses absolute time for delayed execution
                - A SEND_DELAYED message can be implemented in supercollider
                    + Would remove need for delay arg in other messages
                    + Would remove need for note_on_timed altogether
                    + Can be a bundle with many messages
                    + Can be interpreted by other applications
                    + Can probably be implemented as native supercollider code, somehow 
                        -> See: read_scd  
                        -> It's possible that a native "beat delay" or "sec delay" already exists, as opposed to 
                            calculating time from beats. 
                    - Does not solve issue with wanting absolute time of execution
                - Getting around the sequencer limitation: 
                    - Messages can pre-calculate their intervals...
                        ... but then the sequencer bpm changes ...  
                    - Sequencer can append info to messages sent as "send_time" 
                        - Sadly, this would mean another wrapping of the message and more confusion in the router
                        - Not necessarily a performance hog or inconvenience, but the gain would have to be very clear 
                            for this to be worth it  

        - CPU Usage
            - input_lab sits at a constant 33% and makes the fans run 
            - input_lab also struggles to produce the stringify it beomes very long
                -> Ideally this hsould be threaded - there's no need to stringify while trying to play 
                -> Another thread, a stringify flag in state, off ye go 
                    -> Sometihng something don't lock keys while performing stringify 
            - Sequencer eats a decent amount of CPU even when stopped
                -> Ideally it should have some kind of dead-poll that is a lot slower than the current 4ms 
            

        - Vector Queues
            ?? To facilitate drum breaks and smoother jamming of longer songs
            - STEPS:
                1. Implement support in sequecer, but with the queue always being a singleton list
                2. Change sequencer queue message to contain a list, then change pycompose and tests to use a singleton queue list


                4. Add support in pycompose for splitting queues into separate sections 
                5. Add support in pycompose for the now different queue and nrt messages 
        
        - Entry point messages
            ?? Because we might want manually defined points where new queues can start 
            ?? Because it's a quicker way to implement some of the value of vector queues 
            - So: 
                - Sequencer receives a message that says "entry toggle" (basically sends to itself)
                - A switch is flipped so that a single start is possible, after which the switch goes off again 

        - Knobstation
            ?? To have some fun with the Minilab 
            - STEPS:
                1. Add a knobreader application, similar to the keyboard, that detects input via the Minilab
                2. Add OSC configuration for binding specific knobs to specific buses 

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
