# Testing grounds 
from jdw_client import JDWClient
from osc_transform import SendType


client = JDWClient() 

"""

    ### SYNTAX GUIDE

    # synth:alias = play string
    tracks["gentle:gentle2"] = "c c d _ f e g :: #.4 >.1"

    # simple prefix to allow samples
    tracks["SP_KayR8:drum1"] = "bd1 bd2 :: =0.5"

"""
tracks = {}


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
#tracks["SP_Roland808:drum5X"] = "bd6 sn7[=0.25] bd7[=1] to[=0.25] (sn4/sn8)[=1.5] :: ofs0.001 rate1.2"
#tracks["SP_Roland808:drum4X"] = " (mi18/mi12)[=3.75] (mi43/mi48)[=0.25 #0.2] :: ofs0.001 rate4"
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

# Raddest track yet 
#tracks["SP_Roland808:drum5X"] = "bd6 sn7[=0.25] bd7[=1] to[=0.25] (sn4/sn8)[=1.5] :: ofs0.001 rate1.2"
#tracks["SP_Roland808:drum4X"] = " (mi18/mi12)[=3.75] (mi43/mi48)[=0.25 #0.2] :: ofs0.001 rate4"
#tracks["SP_Roland808:drum3X"] = "bd3[rate1] (mi3[#0.7]/sn3) :: ofs0.00 rate1"
#tracks["eli:plucker"] = "d4[=0.25] g3[=0.25] g2[fx0.4] g3[=0.25] d3[=0.25] (f3/d4/c3/g2)[fx0.6 cut1800 #0.3] c4[fx0.4] :: >1 =1 #1 fx0"
#tracks["eli:plucker"] = "d3[=0.25] g3[=0.25] g2 g3[=0.25] d3[=0.25] (g2/f3/d4/c3) c2 :: >1 =1 #1"
#tracks["elisin:roar"] = " d3[cut800 #0.7] c4 g3 c3 :: >8 =8 #1"

# Theseus 
tracks["pycompose:bassline"] = "Mg3 b3 b3 g3 b3 b3 g3 b3 g3 b3 b3 c4 b3 g3 a3 g3 {} g3 c4 c4 g3 c4 c4 g3 c4 g3 c4 c4 d4 c4 g3 b3 g3  :: =0.5 >0.6 #0.2 relT2.2 fmod1 fxf500 fxs0.2 fxa0.4 cutoff1300"
tracks["brute:rapapa"] = "g2 {x32} c2 {x32} g2 {x32} d3 {x32} :: >0.06 =0.25 #0.2"
tracks["brute:rapapaaaaa"] = " c4 c3 {x16} g4 g3 {x16} c4 {x32} g4 g3 {x16} :: >0.2 =0.25 #0.08"
tracks["SP_Roland808:drum5X"] = " (bd2/(bd2 bd2)[=0.25] bd2[=1.5]) sn3[ofs0.02]  :: =2 rate2 ofs0"
tracks["elisin:roar"] = " d4 d4[=4] c4[=4] g3 c4[=2] b3[=6] :: >8 =8 #0.2 cut450"

client.read_custom_synths()
#client.stop() #
client.set_sequencer_bpm(108)


for key in tracks:
    contents = key.split(":")
    synth_name = contents[0]
    is_sample = "SP_" in synth_name
    synth_name = synth_name.split("SP_")[1] if is_sample else synth_name
    send_type = SendType.PLAY_SAMPLE if is_sample else SendType.NOTE_ON_TIMED

    alias = contents[1] if len(contents) > 1 else contents[0] # Default to name of the synth 
    parse_string = tracks[key]

    print("string: ", parse_string, " synth_name: ", synth_name, " alias: ", alias)

    #Synth(parse_string, alias, sc_synth_name=synth_name, default_send_type=send_type).play()
    client.play(synth_name, parse_string, alias, default_send_type=send_type)


# Jan 2024 Notes 
"""

Chronological default args:
- d6[::amp0.2] d3 d2 d3 d4[::amp0.2] d2
- Basically: "From this note, until otherwise specified, use the following defaults"

"""