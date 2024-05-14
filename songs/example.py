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
        # TODO: Implement support for "n_free" via regex, which would allow us to resend this infinitely 
        jdw_osc_utils.create_msg("/note_on", ["reverb", "reverb_effect_1", 0, "inBus", 4.0, "outBus", 0.0]),
        jdw_osc_utils.create_msg("/note_on", ["control", "cs", 0, "bus", 55.0, "prt", 0.5]),
        jdw_osc_utils.create_msg("/note_modify", ["reverb_effect_1", 0, "mix", 0.63, "room", 0.75])
        # Control bus example 
        #jdw_osc_utils.create_msg("/c_set", [44, -4.0])

    ]

def configure():

    client = my_client.get_default()

    client.send(jdw_osc_utils.create_msg("/set_bpm", [116]))

    configure_keyboard.as_synth(2, "pycompose")
    #configure_keyboard.as_sampler("EMU_EDrum") 

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

    client.send_message("/wipe_on_finish", [])

    #tracks["metronome:SP_Roland808"] = "(56 x 56 x 56 x 56 40):ofs0"
    
    """
    
        YES HELLO THIS IS FEATURE PLANNING AGAIN


        - Vector Queues
            ?? To facilitate drum breaks and smoother jamming of longer songs
            - STEPS:
                1. Implement support in sequecer, but with the queue always being a singleton list
                2. Change sequencer queue message to contain a list, then change pycompose and tests to use a singleton queue list
                3. Extend sequencer is_finished and reset logic to fully accomodate the new queue logic
                4. Add support in pycompose for splitting queues into separate sections 
                5. Add support in pycompose for the now different queue and nrt messages 
        
        - Note killing
            - See n_free note above regarding zero-time messages 

        - Keyboard Key Release 
            ?? To make it more vibrant, with better chord/pads support 
            - STEPS:
                1. Write these steps (note_on, release update history, late release not a problem)

        - Keyboard Track Printing
            ?? To streamline keyboard usage and lower the bar for track jamming
            - STEPS:
                1. Add key detection for CTRL+NUM 
                2. Construct a track name as keyboard_NUM:<SP_?><instrument_name> and paste full chunk to clipboard

            -> Future: track logging and instant sending

        - Knobstation
            ?? To have some fun with the Minilab 
            - STEPS:
                1. Add a knobreader application, similar to the keyboard, that detects input via the Minilab
                2. Add OSC configuration for binding specific knobs to specific buses 
                3. Wire up some synth to have a knob bus mod e.g. LFO

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
                        - And things like "play this track 3 times, and play these other tracks alongside it"
                    - .break(name, parse, peers) can be a way of saying "play this once, creating a track for it at this time, with peers playing along"
    
        - Documentation and other Boring Stuff
            - shuttle notation (once we're happy with the syntax)
            - sequencer lib (no blocker)
            - jdw sc error proofing
            - sequencer and sc OSC-driven-configuration
    
    """


    # SAVAGE
    tracks["savage:SP_EMU_EDrum"] = "(16:0.75 16:0.75,rate0.99 16:1 16:0.5,rate0.3 16:1,rate0.4):ofs0,sus0.5,amp1,relT0.5,len4"
    tracks["drama:SP_EMU_EDrum"] = "(36:0.5 36:0.5 40:1 36:1 40:1 36:0.5 36:0.5 40:1 36:0.5 40:0.5 36:0.5 40:0.5):amp1,ofs0,relT0.5,sus0.5,len8.0"
    tracks["ad:pycompose"] = "(eb3:0.74 eb3:0.72 eb3:2.51 g3:0.74 g3:0.73 eb3:2.56):amp1,ofs0,relT0.5,sus0.5,len8.00"
    tracks["fill:pycompose"] = "(eb4:0.7 bb3:0.74 eb4:0.52 bb3:2.04):ofs0,sus0.1,relT2,amp1,len4.00"
    tracks["ruff:pycompose"] = "(x:32 eb6:0.79 eb6:0.7 eb6:0.5 eb6:0.76 bb5:0.73 ab5:0.53 g5:0.78 ab5:0.64 bb5:0.64 ab5:1.98 eb6:0.74 eb6:0.66 eb6:0.56 eb6:0.79 bb5:0.7 ab5:0.55 bb5:3.93 eb6:0.81 eb6:0.65 eb6:0.56 eb6:0.74 bb5:0.72 ab5:0.54 g5:0.75 ab5:0.69 bb5:0.58 ab5:1.01 eb5:1.01 eb5:0.78 eb5:0.67 g5:0.54 ab5:0.66 bb5:0.73 ab5:0.54 g5:0.04 x:4):relT1.5,sus0.5,ofs0,amp1,len28.00"

    #tracks["notememe:pycompose"] = "((26 / 27):0.75 26:0.75 26:2.5):bus4"
    #tracks["notememe3:pycompose"] = "(62:0.75 69:0.25 69:0.5 69:1 67:0.5 (69 / 65 / 69 / 62):1):relT1"
    #tracks["notememe4:pycompose"] = "(0:1 62:0.5 62:0.5 62:0.5 62:1.5):relT2"
    #tracks["schre:pycompose"] = "(105:1 105:3 0:4):sus1,relT3,amp1"
    #tracks["meme:SP_Roland808"] = "(0:0.75 25:0.75 0:1 25:0.5 0:0.5 25:0.5):ofs0"
    #tracks["meme2:SP_Roland808"] = "(38:0.25 38:3.75):ofs0"
    #tracks["meme3:SP_Roland808"] = "(51:0.25 51:0.5 51:3.25);ofs0"


    # Sequencer queue 
    for bundle in tracks.into_sequencer_queue_bundles():
        client.send(bundle)
        pass 

    # NRT Record 
    for bundle in tracks.into_nrt_record_bundles(one_shot_messages):
        #client.send(bundle)
        pass 