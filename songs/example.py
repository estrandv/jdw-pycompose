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
        jdw_osc_utils.create_msg("/note_on", ["reverb", "reverb_effect_1", 0, "inBus", 4.0, "outBus", 0.0, "mix", 0.34, "room", 0.24]),
        jdw_osc_utils.create_msg("/note_on", ["reverb", "reverb_effect_2", 0, "inBus", 5.0, "outBus", 0.0, "mix", 0.94, "room", 0.64]),
        jdw_osc_utils.create_msg("/note_on", ["control", "cs", 0, "bus", 55.0, "prt", 0.5]),
        jdw_osc_utils.create_msg("/note_on", ["brute", "bdr", 0, "amp", 0.0]),
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

    # TODO: pycompose does not have a working gate setting, sadly

    # Drum presets 
    configure_keyboard.as_sampler("EMU_EDrum")

    # TODO: All messages can be shuttle string billboards 

    # Low cutoff pycompose is good bass! 
    #configure_keyboard.as_synth(2, x:16 "pycomp7se", a16gs=["amp", 1.5, "att", 0.2, "relT", 0.1, "fxa", 22.4, "cutoff", 200.0])
    
    #configure_keyboard.as_synth(5, "pluck", args=["amp", 0.6, "att", 0.0, "relT", 0.8, "fxa", 22.4])
    configure_keyboard.as_synth(5, "FMRhodes", args=["amp", 0.6, "att", 0.0, "relT", 0.8, "fxa", 22.4])
    #configure_keyboard.as_synth(4, "brute", args=["amp", 0.1, "attT", 0.0, "relT", 4.8, "fx", 2.002, "hpf", 7300.0])
    #configure_keyboard.as_synth(4, "brute", args=["amp", 0.1, "attT", 0.0, "relT", 0.8])
    #configure_keyboard.as_synth(4, "gentle", args=["amp", 0.1, "att", 0.2, "relT", 0.1, "fxa", 22.4])
    #configure_keyboard.as_synth(4, "feedbackPad1", args=["amp", 0.4, "relT", 10.1, "fxa", 22.4, "cutoff", 200.0, "fbAtt", 0.0])

    #tracks["metronome:SP_Roland808"] = "(56 36 56 36 56 36 56 40):ofs0"

    # TODO: Fix wrong octave in keyboard-based keys app 

    # TODO: Sampler doesn't allow different tracks to run thei own args, for some reason
    #   - s_new is used, so that's not the problem
    #   - could be some fine print in the sampler def
    #   - Could be something happening here - investigate result of send_jam when multiple sampler runs 

    # TODO: Nice-to-haves
    #   - Full-octave transpose, outside of shuttle 
    #   - Easier synth switching, ideally without having to move the cursor from the billboard 


    # TODO: Road ahead for track groups
    #   - Still missing a good way to do "break right before new track" without heavily duplicating things
    #   - Still missing an easy way to say "replace this track" in order to avoid waiting for start (man ext id?)

    # TODO: Negative arg values don't work
    #   - "-0.2" is interpreted as a relative reduction, not a flat negative. 

    billboard = """

    ### Billboard quirks
    # Tracks are named based on their line index and should not be moved around after being defined

    ### Billboard symbols 
    # '@' denotes 'use this synth for below lines'
    # '#' denotes comment line
    # '<N>' as first text adds the track to group 'N'
    # '>>>123' defines which groups should be included (others behave as if commented)
    
    ### Note symbols 
    # '§' denotes loop start time for keyboard

    #>>> a y
    #>>> D d b a
    #>>> b D d a o y
    #>>> b D d a r
    #>>> d b a y f
    #>>> b D d c a s r y
    #>>> b D d c a s r y z
    #>>> a o r b s f
    #>>> a o d z

    @FMRhodes
    <s> (a6:0.5,sus0.5 e7:1,sus0.5 a6:0.5,sus0.5 e7:1,sus0.5 f7:0.5,sus0.25 e7:0.5,sus0.25 c7:0.5,sus0.25 e7:0.5,sus0.25 f7:0.5,sus0.25 e7:0.5,sus0.25 g7:1,sus0.5 f7:1,sus0.25 e7:0.5,sus0.25 d7:1,sus0.25 e7:0.5,sus0.25 c7:1,sus0.25 d7:0.5,sus0.25 e7:1.5,sus0.25 e7:0.5,sus0.25 d7:0.5,sus0.25 c7:1,sus0.5 d7:1,sus0.25 a6:0.5,sus0.5 e7:1,sus0.5 c7:0.5,sus0.25 e7:1,sus0.25 f7:0.5,sus0.25 e7:1,sus0.25 g7:1,sus0.25 g7:0.5,sus0.25 g7:0.75,sus0.25 e7:0.75,sus0.25 d7:0.5,sus0.25 e7:1,sus0.25 . c7:0.5,sus0.25 d7:0.5,sus0.25 e7:1,sus0.25 c7:0.5,sus0.25 d7:0.5,sus0.25 e7:0.5,sus0.25 c7:0.5,sus0.25 d7:0.5,sus0.25 e7:0.5,sus0.25 c7:1,sus0.5 a6:0,sus0.5 x:1):amp0.3,att0,relT0.8,fxa22.4,len32,tot31.25,pan-0.3
    <z> (a5:0.5,sus0.5 e5:0.5,sus0.5 f5:0.5,sus0.5 g5:0,sus0.5 x:0.5):relT0.8,amp0.13,fxa22.4,att0,len4.0,tot1.50,pan0.5

    @pluck
    <r> (e7:3,sus0.5 f7:0.5,sus0.25 e7:0,sus0.25 x:12.5 e7:3,sus0.25 c7:0.5,sus0.25 a6:0,sus0.25 x:12.5):amp0.2,relT0.8,att0,fxa22.4,len4.0,tot3.50,pan0.5
    
    @brute
    <r> x:8 (a5:0.5,sus0.25 e5:0.5,sus0.25 f5:1,sus0.25 e5:0.5,sus0.25 a5:1,sus0.25 e5:0.5,sus0.25 g5:0.5,sus0.25 e5:0.5,sus0.25 f5:1,sus0.25 e5:0,sus0.5 x:2):amp0.08,attT0,relT0.8,len8,tot6.00

    #g4:4,sus0.2,fBus2,amp0.2,relT2,attT0.2,lfoD1,lfoS1,lfBS2,lfBD3

    @SP_EMU_EDrum

    <D> (33:1.5,rate1.95 33:1,rate1.4 x:0.25 34:0.25 33:1,rate0.9)

    <m> (14 14 14 23):1,sus4

    @pycompose
    <a> (a5 a5 b6 c5 c6 a5 a5 (c5 / e6)):amp0.16,bus4
<b> (a3:0.75,sus0.25 a3:0.75,sus0.25 a3:1,sus0.25 a3:0.5,sus0.25 c4:0.5,sus0.25 d4:0.5,sus0.25 a3:0.75,sus0.25 a3:0.75,sus0.25 a3:1,sus0.25 a3:0.5,sus0.25 g3:0.5,sus0.25 f3:0,sus0.25 x:0.5):att0.2,relT0.1,amp1.5,fxa22.4,cutoff119,len8,tot7.50,pan0.05

    @SP_Roland808
<d> (24:0.75 24:0.75 24:0.5 24:0 x:2):att0,amp0.6,relT0.8,fxa22.4,len4.0,tot2.00,ofs0.02,sus0.1,pan-0.26
<d> (x:0.75 x:0.75 26:1 26:0.5 26:0 x:1):att0,amp0.5,relT0.8,fxa22.4,len4.0,tot3.00,rate1.3
#<d> (x:0.75 x:0.75 74:1 74:0.5 74:0 x:1):att0,amp0.1,relT0.8,fxa22.4,len4.0,tot3.00,rate0.9,sus5,bus4,ofs0



    <c> ((x:1 28:1)*4):ofs0,sus4,bus4,amp0.3
    #<5> (x:7.5 27:0.5 (x:1 28:1)*4):ofs0,sus4,bus4
    #<d> (x:3.5 27:0.5):att0,fxa22.4,amp0.6,relT0.8,len4.0,tot0.00 

    <y> (x:31 33:1):relT0.8,fxa22.4,amp0.6,att0,len4.0,tot0.00,sus10,bus4

    @feedbackPad1
    <f> (x:7 a3:1 a4:0 a5:0 x:8):fbAtt0,fxa22.4,amp0.002,relT10.1,cutoff200,len4.0,tot0.00,sus5
    
    @gentle
    <o> (c7:2 a6:1 g6:1 e7:1.5 c7:0 x:10.5 c7:2 a6:1 g6:1 a6:1.5 g6:0 x:10.5):att0.2,relT0.8,amp0.1,fxa22.4,len8,tot5.50,sus0.5,bus4,pan-0.8

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
