# Testing grounds 
from osc_transform import SendType, create_msg, MessageWrapper, to_timed_osc
from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
import parsing
from pythonosc import udp_client
import uuid


client = udp_client.SimpleUDPClient("127.0.0.1", 13339) # Router


class Synth():
    def __init__(self, parse: str, ext_id = "", default_send_type = SendType.NOTE_ON_TIMED, sc_synth_name = "example"):

        self.ext_id = "autogen_queue_id_" + str(uuid.uuid4()) if ext_id == "" else ext_id
        self.default_send_type = default_send_type
        self.sc_synth_name = sc_synth_name

        messages = parsing.full_parse(parse)

        self.msg_wrappers = []
        for msg in messages: 
            msg.add_missing_args({"time": 1.0, "gate_time": 0.1, "amp": 1.0})
            self.msg_wrappers.append(MessageWrapper(msg))

    def id(self, new_ext_id: str):
        self.ext_id = new_ext_id
        return self 

    def nrt_record(self):
        main_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

        note_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        
        timeline = 0
        for wrapper in self.msg_wrappers:

            osc_msg = wrapper.to_osc(self.default_send_type, self.sc_synth_name)
            timed_osc_msg = to_timed_osc(wrapper.get_time(), osc_msg)
            note_bundle.add_content(timed_osc_msg)
            timeline += wrapper.get_time()

        main_bundle.add_content(create_msg("/bundle_info", ["nrt_record"]))
        # TODO: BPM and project output 
        main_bundle.add_content(create_msg("/nrt_record_info", [110.0, "/home/estrandv/jdw_output/" + self.ext_id + ".wav", timeline]))
        main_bundle.add_content(note_bundle.build())

        client.send(main_bundle.build())

    def play(self):

        main_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        # NOTE: Meta-info for the update-queue command, mainly the external id of the sequencer 

        note_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        for wrapper in self.msg_wrappers:

            osc_msg = wrapper.to_osc(self.default_send_type, self.sc_synth_name)
            timed_osc_msg = to_timed_osc(wrapper.get_time(), osc_msg)
            note_bundle.add_content(timed_osc_msg)

        main_bundle.add_content(create_msg("/bundle_info", ["update_queue"]))
        main_bundle.add_content(create_msg("/update_queue_info", [self.ext_id]))
        main_bundle.add_content(note_bundle.build())

        client.send(main_bundle.build())

"""

    ### TYPING COMFORT: Yet another run

    ### SYNTAX GUIDE

    # synth:alias = play string
    tracks["gentle:gentle2"] = "c c d _ f e g :: #.4 >.1"

    # simple prefix to allow samples
    tracks["SP_KayR8:drum1"] = "bd1 bd2 :: =0.5"

"""
tracks = {}

#client.send(create_msg("/hard_stop", []))


# CUTE LIL PIANO 
#tracks["example:piano"] = "d3[=0 >2] d4 d4 g4 d4 c3[=0 >2] c4 c4 d4 c4 f3[=0 >2 #0.2] f4 f4 c4 f4 c3[=0 >2] c4 c4 (d4 / (d4 d4)[=0.5]) c4 :: =1 #0.3 >0.1"

# CUTE LIL TRACK 
#tracks["SP_KayR8:drum1"] = "bd1 hh1 bd2 hh1 :: ofs0"
#tracks["SP_KorgT3:drum2"] = "_ hh0 _ hh1 :: ofs0.0 #0.4"
#tracks["brute:rapzzzz"] = "eb2 {x8} g2 {x8} c3 {x8} ab2 {x8} :: >0.1 =0.5 #0.3"
#tracks["brute:test"] = "c4 :: >0.1 =1 #0.2"
#tracks["example:rapx"] = "eb1 {x16} g1 {x16} c2 {x16} ab1 {x16} :: >0.2 =0.25 #0.2 pan-0.2"
#tracks["brute:rap2"] = "eb3 g3 c3 ab3 :: >2 =4 #0.2"
#tracks["gentle:sing"] = "g5 g5 g5 (eb5 (ab5/d5))[=2] :: =4 >1.2 relT0.5 attT0.01 #0.1"
#tracks["pluck:raapapa"] = "g5[=0.5] f5[=0.5] g5[=0.5] f5[=2.5] ((g5 g#5)[=0.5] _ g5[=2] / d#5[=4]) :: >0.1 attT0.4 relT3.5 #0.4"
#tracks["SP_Roland808:drumX"] = " (mi11 / mi5)[#0.3] sn8 _ sn8 _ sn1 _ (sn8 sn3 _ _)[=0.25] :: ofs0.022 rate0.5"
#tracks["SP_Roland808:drum2X"] = "bd5 _ (bd4 bd8)[=0.5] mi4[#0.2] bd0 mi4[#0.2] bd1 _ :: ofs0.002 rate1"

# Another track 
#tracks["SP_Roland808:drum2X"] = "bd5 sn4 {x3} bd5 (sn4 sn5)[=0.5] :: ofs0.002 rate1"
#tracks["SP_Roland808:drum3X"] = " (mi11/mi23)[=8] :: ofs0.002 rate1"
#tracks["SP_Roland808:drum4X"] = " _[=3.75] (mi43/mi48)[=0.25 #0.2] :: ofs0.001 rate4"
#tracks["brute:rap"] = "eb3 g3 d4 {x4} c4 f4 eb4 d3 {} eb3 g3 d4 {x4} _[=2] :: >0.2 =0.5 #0.3 relT0.8  fx12"
# TODO: Sawbass has a memory leak 
#tracks["example:rapapa"] = "eb4 g3 {x8} d4 g3 {x8} c4 g3 {x8} d4 g3 {x8} :: >0.06 =0.25 #0.2"

# Yet another (works well with the pycompose one below) 
#tracks["pluck:raapapa"] = "c6 d6 f5 d6 :: relT5 =4"
#tracks["pluck:raapapaasdasd"] = "g5 g5 c5 c5 a5 a5 c5 c5 :: >4 relT6 =2 #0.4"
tracks["SP_Roland808:drum5X"] = "bd6 sn7[=0.25] bd7[=1] to[=0.25] (sn4/sn8)[=1.5] :: ofs0.001 rate1.2"
tracks["SP_Roland808:drum4X"] = " (mi18/mi12)[=3.75] (mi43/mi48)[=0.25 #0.2] :: ofs0.001 rate4"
#tracks["example:rapapazz"] = "c3 g3 {x8} d4 g3 {x8} :: >0.06 =0.25 #0.2"
#tracks["brute:rapapazzaa"] = "c3 f2 c3 g2 :: >4 =8 relT8 #0.4 lfoS0.1 lfoD0.01 fx0.06"

# TODO: Easiest way to selectively mute tracks: 
# All tracks should come at once, as a batch send of queue messages in a bundle 
# Then you can have a sequencer mode that says "Wipe tracks not present in new queue payload"
# This wipe would have to be "On next finish", of course. New boolean flag inside sequencer..? 

# More experimenting 
#tracks["pycompose:testingreadscd"] = "c6 d6 f5 d6 :: >4 relT5 =4 fmod0.5"
#tracks["pycompose:testingreadscddd"] = "eb2[=0] eb3 {x8} c3[fxs0.8] {x8} g3[fxb0.3] {x8} d3[fxf200 fxs0.6] {x8} :: >1 =0.25 #0.2 relT0.4 fmod1"
#tracks["SP_Roland808:drum4X"] = "bd11[rate2] sn8 {x3} bd4 (sn8 sn8[ofs0.002])[=0.25 rate0.5] _[=0.5] :: ofs0.00 rate1"
#tracks["filtersquare:plucker"] = "c2 d3[=0.25] g3[=0.25] g2 f3 g3[=0.25] d3[=0.25] (g2/f3/d4/c3) :: >0.124 =0.5 #1 relT0.1 fmod2"


#tracks["SP_Roland808:drum4X"] = "bd3[rate1] (mi3[#0.7]/sn3) :: ofs0.00 rate1"
tracks["eli:plucker"] = "d4[=0.25] g3[=0.25] g2[fx0.4] g3[=0.25] d3[=0.25] (f3/d4/c3/g2)[fx0.6 cut1800 #0.3] c4[fx0.4] :: >1 =1 #1 fx0"
#tracks["eli:plucker"] = "d3[=0.25] g3[=0.25] g2 g3[=0.25] d3[=0.25] (g2/f3/d4/c3) c2 :: >1 =1 #1"
#tracks["eli:plucker2"] = " d5:a eb4 g5:a c4[=1]  :: >4 =4 #1"
tracks["elisin:roar"] = " d3[cut800 #0.7] c4 g3 c3 :: >8 =8 #1"

with open("synthdefs/pycompose.scd", "r") as file:
    data = file.read() 
    client.send(create_msg("/read_scd", [data]))

for key in tracks:
    contents = key.split(":")
    synth_name = contents[0]
    is_sample = "SP_" in synth_name
    synth_name = synth_name.split("SP_")[1] if is_sample else synth_name
    send_type = SendType.PLAY_SAMPLE if is_sample else SendType.NOTE_ON_TIMED

    alias = contents[1] if len(contents) > 1 else contents[0] # Default to name of the synth 
    parse_string = tracks[key]

    print("string: ", parse_string, " synth_name: ", synth_name, " alias: ", alias)

    Synth(parse_string, alias, sc_synth_name=synth_name, default_send_type=send_type).play()


client.send(create_msg("/set_bpm", [100]))


# Jan 2024 Notes 
"""

Chronological default args:
- d6[::amp0.2] d3 d2 d3 d4[::amp0.2] d2
- Basically: "From this note, until otherwise specified, use the following defaults"

"""