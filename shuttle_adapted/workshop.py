from shuttle_notation import Parser, ResolvedElement
from decimal import Decimal
from pythonosc import osc_message_builder, udp_client, osc_bundle_builder
from pythonosc.osc_packet import OscPacket
from jdw_tracking_utils import Tracker

import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils
import configure_jdw_sc


"""

This file aims to contain everything needed to parse and send messages to the router. 

FEATURE BRAINSTORMING:
    - MIDI TONE SAMPLES
        - Add a custom interpretation for play_sample where elements that conform to the letterNumber standard can be interpreted as tone indices 
        - This would allow us to take a midi instrument, convert it to samples, and play it in supercollider like any other sampler synth 
    - DESIGN PHILOSOPHY: WHO OWNS SYNTHDEFS? 
        - Currently, JDW-SC maintains a list of recorded synthdefs, which is then also uses for NRT 
        - This makes synth definition very convenient, BUT: 
            - Since we have zero-time messages, we could just as well populate that here without forcing SC to record anything 
            - (JDW-SC would thus just take a bunch of read_scd messages that we configure here)
        - One argument against removing it in JDW-SC is:
            - Sampler and sample resolution is today baked in there, due to how buffers work 
            - So it's nice when things work in a similar way (we will not bake sampler stuff into pycompose..?)
    - ALTERNATIONS QUIRKS 
        - Note that repeating alternations can get weird when you "consume" all alternations by repeating 
        - This is acceptable, but also means that you cant wrap long sections in repeats to create longer tracks 
            - As such, it becomes necessary to include a second definition of repeat: "repeat up until here AFTER resolving all elements"
                - This can be a custom definition here in pycompose 
    - TRACK MERGING
        - For example: when you've made chords or complex drum riffs using multiple tracks, and you want the NRT wav to at least be the same file 
            - 

ONGOING TODOS:
    - Lib separation
        - Parsing and jdw-interpretation separated into its own submodule
        - Should also separate the utils, like tracker, into its own separate module
        - A "jam repo" should ideally only contain server_config and jam_file
    - Effect Synths
        - Still no groups separation of new nodes; effects should be in group 0 (before) and notes in group 1 (after)

"""


client = udp_client.SimpleUDPClient("127.0.0.1", 13339) # Router

# Wipe on finish example
client.send(jdw_osc_utils.create_msg("/wipe_on_finish"))

# Custom scd example
#with open("synthdefs/pycompose.scd", "r") as file:
#    data = file.read() 
#    client.send(create_msg("/read_scd", [data]))

# {synth_name:parse_string}
tracks = Tracker() 
tracks.parser.arg_defaults = {"time": Decimal("0.5"), "sus": Decimal("0.2"), "amp": Decimal("0.5")}

# Stop sequencer example
#client.send(create_msg("/hard_stop", []))

# (Messages that are sent immediately; not part of a sequence, that should also be included in any eventual NRT record message)
zero_time_messages = []
zero_time_messages.append(jdw_osc_utils.create_msg("/note_modify", ["reverb_effect_1", 0, "mix", 0.63, "room", 0.75]))
# Control bus setting example - synths can use In.kr(bus) to read val!
#zero_time_messages.append(jdw_osc_utils.create_msg("/c_set", [44, -4.0]))
# Drone example
#zero_time_messages.append(jdw_osc_utils.create_msg("/note_on", ["pycompose", "drone", 0, "bus", 4.0, "amp", 1.0, "sus", 10.0]))

# Send before anything else 
for msg in zero_time_messages:
    client.send(msg)

# Example regular synth
# Note special jdw characters: "x" is EMPTY, "." is IGNORE/SPACER

### DEMO 
#tracks["somedrumYO:SP_[KB6]_EMU_E-Drum"] = "(12 x 17 x ):ofs0,bus4,amp1"
#tracks["basicbass:pycompose"] = "(g2*16 d2*16 c2*16 d2*8 c2*8):0.5,sus0.3,relT0.5,fBus55"
#67:0.875 62:0.625 67:1 62:0.5 67:1 67:1.5 69:1.375 67:1 67:1 62:0.5 67:1 62:0.5 67:1 67:1.625 71:1.375 69:1.125
tracks["riff:pycompose"] = "(67:0.875 62:0.625 67:1 62:0.5 67:1 67:1.5 69:1.375 67:1 67:1 62:0.5 67:1 62:0.5 67:1 67:1.625 71:1.375 69:1.125):relT2"

# TODO: These INDEX-based notes appear not to respect the "x" symbol properly 
#tracks["metronome:SP_[KB6]_EMU_E-Drum"] = "(12 x 12 x 12 x 17 x):ofs0"
#tracks["chordififi:pycompose"] = "(60:0.125 64:3.875 60:0 65:4 62:0.125 60:4 65:0 60:2 64:0 60:1.875):relT2"
#tracks["notememe:pycompose"] = "(60:0.5 65:0.5 65:0.5 60:0.25 65:0.5 65:0.5 60:0.25 65:0.5 65:0.5):relT0.5"

tracks["notememe:pycompose"] = "((26 / 27):0.75 26:0.75 26:2.5):bus4"
#tracks["notememe3:pycompose"] = "(62:0.75 69:0.25 69:0.5 69:1 67:0.5 (69 / 65 / 69 / 62):1):relT1"
#tracks["notememe4:pycompose"] = "(0:1 62:0.5 62:0.5 62:0.5 62:1.5):relT2"
#tracks["schre:pycompose"] = "(105:1 105:3 0:4):sus1,relT3,amp1"
#tracks["meme:SP_Roland808"] = "(0:0.75 25:0.75 0:1 25:0.5 0:0.5 25:0.5):ofs0"
#tracks["meme2:SP_Roland808"] = "(38:0.25 38:3.75):ofs0"
#tracks["meme3:SP_Roland808"] = "(51:0.25 51:0.5 51:3.25);ofs0"

# Example of a control bus modifier - synths can use In.kr(bus) to read val!
#tracks["cseq:control"] = "(0@cs:val200 0@cs:val0):16,bus55,prt8"

#tracks["somedrumYO:SP_[KB6]_EMU_E-Drum"] = "(12 x 17 x 12 12 17 (x / (12 / (to3)*4:0.125))):ofs0,bus4,amp1"
#tracks["basicbass:pycompose"] = "(g2*8):0.5,sus0.3,relT0.5,fBus55"
#tracks["hum:pycompose"] = "(g6:0 d5 c5 d5 (g5 / a5) d5 x g5:4):2,relT4,fx0.5,amp1"
#tracks["dee:pycompose"] = "(x (x / c5) x d5 b4 x g4 x):0.5,relT2.3"
#tracks["chords:pycompose"] = "(d4:8,attT0.5 g4:0,attT0.3 (b4 / c4 / a4 / d3):0,attT0.1,relT6):sus2,relT4,amp0.5,fx0.5"

# NRT Record 
for bundle in tracks.into_nrt_record_bundles(configure_jdw_sc.get_oneshot_messages() + zero_time_messages):
    #client.send(bundle)
    pass 

# Sequencer queue 
for bundle in tracks.into_sequencer_queue_bundles():
    client.send(bundle)
    pass 