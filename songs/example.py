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
        # Note that effects, control tracks and drones all work well in this category
        # Note also that a drone can be launched with amp0 and then modified during sequence tracks as needed 
        # TODO: Some kind of security-note-on would be important here to allow resendability.
        #   As it stands, we're dupicating the reverb effect with each update call 
        jdw_osc_utils.create_msg("/note_on", ["reverb", "reverb_effect_1", 0, "inBus", 4.0, "outBus", 0.0]),
        jdw_osc_utils.create_msg("/note_on", ["control", "cs", 0, "bus", 55.0, "prt", 0.5]),
        jdw_osc_utils.create_msg("/note_modify", ["reverb_effect_1", 0, "mix", 0.63, "room", 0.75])
        # Control bus example 
        #jdw_osc_utils.create_msg("/c_set", [44, -4.0])

    ]

def configure():

    client = my_client.get_default()

    configure_keyboard.as_synth() 

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



    # Send before anything else 
    for msg in zero_time_messages:
        client.send(msg)


    tracks = Tracker() 
    tracks.parser.arg_defaults = {"time": Decimal("0.5"), "sus": Decimal("0.2"), "amp": Decimal("0.5")}

    #tracks["metronome:SP_Roland808"] = "(56 x 56 x 56 x 56 40):ofs0"

    tracks["notememe:pycompose"] = "((26 / 27):0.75 26:0.75 26:2.5):bus4"
    tracks["notememe3:pycompose"] = "(62:0.75 69:0.25 69:0.5 69:1 67:0.5 (69 / 65 / 69 / 62):1):relT1"
    tracks["notememe4:pycompose"] = "(0:1 62:0.5 62:0.5 62:0.5 62:1.5):relT2"
    tracks["schre:pycompose"] = "(105:1 105:3 0:4):sus1,relT3,amp1"
    tracks["meme:SP_Roland808"] = "(0:0.75 25:0.75 0:1 25:0.5 0:0.5 25:0.5):ofs0"
    tracks["meme2:SP_Roland808"] = "(38:0.25 38:3.75):ofs0"
    tracks["meme3:SP_Roland808"] = "(51:0.25 51:0.5 51:3.25);ofs0"


    # Sequencer queue 
    for bundle in tracks.into_sequencer_queue_bundles():
        client.send(bundle)
        pass 

    # NRT Record 
    for bundle in tracks.into_nrt_record_bundles(one_shot_messages):
        #client.send(bundle)
        pass 