from shuttle_notation import Parser, ResolvedElement
from decimal import Decimal
from pythonosc import osc_message_builder, udp_client, osc_bundle_builder
from pythonosc.osc_packet import OscPacket
from jdw_tracking_utils import Tracker

import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils
import configure_jdw_sc

#####################################

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

ONGOING TODOS:
    - Create a library, so that jams can be in their own repo 
        - Question is: what is library, what is jam? 
            - The library core should always be "JDW interpretation of Shuttle Notation"
                - That is: taking elements and converting them into JDW-compatible messages
                - This includes custom definitions such as "x" for silence
        - A jam is everything else!
            - Tracker, client, definitions, whatever 
        - This means that the library should not contain CLIENTS, but can contain MESSAGE DICTS
            - So "get bpm message" is a valid library function 

    => IMplementation 
        - We can separate the jdw-shuttle-lib-py utilities into a new repo and keep the current one as the jam repo 
            - Since everything is a mess, it's fine to start with separating into two dirs: JAM and LIB

FEATURE BRAINSTORM:
    - Effects! 
        - TODO: 
            1. bus stack and an "assert buses" call that makes sure a certain amount of buses are loaded 
                - I've added a hardcode of bus creations in the NRT script, via native loop which is clean 
                - There seems to be some buses available from the get go, as bus 4 was usable as a reverb bus
                    - UPDATE: default s.numAudioBusChannels=1024, so there is really no need to assert extra buses  
                - Verified that an effect synth (note_on) should be started -before- any other synths (note_on) are created
                    - This will almost always be the case automatically, as new synths play as the sequencer loops
                    - The proper way is of course to have separate groups, with the effects group being created before the synth group
                        and thus located before it 
            2. NRT
                - I think it should just work native (default s.numAudioBusChannels=1024), but I haven't tested NRT yet
                - ON ANOTHER NOTE: effects don't work with nrt yet, since freeform note_on calls are not recorded 
                    -> This is a jdw-pycompose problem; we should record these messages as part of the nrt message package 

                         zero_time_messages = []
                         append(...)
                         

    - LIVEMOD 
        - WHY A MOD LOOKUP IN JDW-SC IS A BAD IDEA: 
            - Every single new note will need to perform a lookup of all mods with all regex matches and modify BEFORE playing 
            - This is infeasible since it introduces vartime in note_on calls
            - It is still, somewhat, feasible to implement some kind of "latency after receiving" logic, but that will in itself
                come with some hurdles and add lots of gnarly code across different message types, 
            - This method also doesn't magically solve things like recording the live mod for NRT, and so on.
        - WHY CONTROL BUSES MIGHT JUST BE A GOOD IDEA 
            - There are tens of thousands of default control buses available without any additional configuration
            - Synthdefs are dynamically defined now and can use bus mods where needed on a make-to-order basis 
            - Which bus number to read from can be supplied as and arg, making the value NOTE-INDIVIDUAL
                ... which works -at least- as well as regex lookup of external ids! 
            - Bus writing has extensive native support and can even be part of other synths
                ... with portamento! 
                ... and their own sequences for NRT!

            # In synthdef
            freq = freq + In.kr(fBus);

            # Setting the bus in a synthdef
            myVal = prt(myVal) ... 
            Out.kr(oBus, myVal)

            # Setting the bus with OSC 
            ["/c_set", fBusIndex, fModValue]

        - REQUIREMENTS
            x1. A synth with an "fBus" index arg and a modification of freq from that value. 
            x2. c_set support in jdw_sc, with the router updated. Simple create_msg() call to it here. 
            x3. (future) experiments with a control bus synth for varied control 

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
zero_time_messages.append(jdw_osc_utils.create_msg("/note_modify", ["reverb_effect_2", 0, "mix", 0.0, "room", 0.75]))
# Control bus setting example - synths can use In.kr(bus) to read val!
#zero_time_messages.append(jdw_osc_utils.create_msg("/c_set", [44, -4.0]))
#zero_time_messages.append(jdw_osc_utils.create_msg("/note_on", ["pycompose", "drone", 0, "bus", 4.0, "amp", 1.0, "sus", 10.0]))

# Send before anything else 
for msg in zero_time_messages:
    client.send(msg)

# Example regular synth
# Note special jdw characters: "x" is EMPTY, "." is IGNORE/SPACER

### DEMO 
#tracks["somedrumYO:SP_[KB6]_EMU_E-Drum"] = "(12 x 17 x ):ofs0,bus4,amp1"
#tracks["basicbass:pycompose"] = "(g2*16 d2*16 c2*16 ab2*8 d2*8):0.5,sus0.3,relT0.5,fBus55"

# Example of a control bus modifier - synths can use In.kr(bus) to read val!
#tracks["cseq:control"] = "(0@cs:val200 0@cs:val0):16,bus55,prt8"

#tracks["somedrumYO:SP_[KB6]_EMU_E-Drum"] = "(12 x 17 x 12 12 17 (x / (12 / (to3)*4:0.125))):ofs0,bus4,amp1"
#tracks["basicbass:pycompose"] = "(g2):0.5,sus0.3,relT0.5,fBus55"
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