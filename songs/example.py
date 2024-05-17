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

    # Low cutoff pycompose is good bass! 
    #configure_keyboard.as_synth(2, "pycompose", args=["amp", 0.8, "att", 0.2, "relT", 0.1, "fxa", 22.4, "cutoff", 200.0])
    configure_keyboard.as_synth(3, "gentle", args=["amp", 0.8, "att", 0.2, "relT", 0.1, "fxa", 22.4, "cutoff", 200.0])
    #configure_keyboard.as_sampler("EMU_EDrum") 

    #tracks["metronome:SP_Roland808"] = "(56 36 56 36 56 36 56 40):ofs0"


    billboard = """
    
    # '@' denotes 'use this synth for below lines'
    # '#' denotes comment line 

    @brute
#(c3:2,sus1.175 g3:1,sus0.4737 e3:0.5,sus0.2863 f3:0.5,sus4.317 x:12 a3:2,sus1.023 e3:1,sus0.5032 f3:0.5,sus0.2383 g3:0.5,sus4.061 x:12):amp0.4,relT0.6,att0.2,fxa22.4,len4.0,bus4



    @pluck

    #g5:amp0.2
    #(g5 d5 c5*2 g5 x d5 x):amp0.2,blur4
    #(c4 c4 c4*2 c4 x c4 x):amp0.2,blur1.4


    @SP_Roland808
#(0:0.75 0:0.75 0:0.5 0:1 0:1):ofs0,amp1,relT0.2,len4




    @feedbackPad1
(c5:4,sus3.753 d6:4,sus1.674 f5:0,sus2.662):amp0.005,relT0.1,att0.2,len8
(f3:0,sus7.410 c3:0,sus7.437 c4:4,sus7.406 x:12):att0.2,relT0.1,amp0.0012,len4



    @pycompose
#(c2:0.75,sus0.09579 a2:0.75,sus0.09592 f2:0.5,sus0.08290 g2:0.75,sus0.1750 a2:0.75,sus0.09980 f2:0.5,sus0.06643 g2:0.75,sus0.09916 a2:0.75,sus0.08132 f2:0.5,sus0.08707 g2:1,sus0.09572 f2:1,sus0.08421):relT0.4,attT0.0,amp1.8,fxa22.4,cutoff200,len8
#(e4:0.75,sus0.09524 c3:0.75,sus0.07052 e4:0.5,sus0.06858 c3:0.5,sus0.07350 e4:0.5,sus0.06529 c3:1,sus0.06663):fxa22.4,att0.2,amp0.8,cutoff200,relT0.1,len4
#(b5:0.25,sus0.09942 c6:0.75,sus0.1254 g5:1,sus0.09975 f5:1,sus0.1074 g5:1,sus0.1461 b5:0.25,sus0.1051 c6:0.75,sus0.07090 g5:1,sus0.1096 d6:1,sus0.09873 c6:1,sus0.1164):att0.2,relT0.3,amp0.7,len8,bus4




    @SP_EMU_EDrum
(20:0.75 20:0.75 20:0.5 20:0.75 20:1.25):amp1,sus0.5,ofs0,relT2.5,len4.00
#(x:1 48:0.5 48:2.5):ofs0,sus0.5,amp1,relT2.5,len4.0




    @gentle




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


        - Vector Queues
            ?? To facilitate drum breaks and smoother jamming of longer songs
            - STEPS:
                1. Implement support in sequecer, but with the queue always being a singleton list
                2. Change sequencer queue message to contain a list, then change pycompose and tests to use a singleton queue list


                4. Add support in pycompose for splitting queues into separate sections 
                5. Add support in pycompose for the now different queue and nrt messages 
        
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
