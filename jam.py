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
#tracks["SP_Roland808:drum1"] = "bd1 hh1 bd2 hh1 :: ofs0"
#tracks["SP_Roland808:drum2"] = "_ hh0 _ hh1 :: ofs0.0 #0.4"
#tracks["brute:rapzzzz"] = "eb2 {x8} g2 {x8} c3 {x8} ab2 {x8} :: >0.1 =0.5 #0.3"
#tracks["brute:test"] = "c4 :: >0.1 =1 #0.2"
#tracks["example:rapx"] = "eb1 {x16} g1 {x16} c2 {x16} ab1 {x16} :: >0.2 =0.25 #0.2 pan-0.2"
#tracks["brute:rap2"] = "eb3 g3 c3 ab3 :: >2 =4 #0.2"
#tracks["gentle:sing"] = "g5 g5 g5 (eb5 (ab5/d5))[=2] :: =4 >1.2 relT0.5 attT0.01 #0.1"
#tracks["pluck:raapapa"] = "g5[=0.5] f5[=0.5] g5[=0.5] f5[=2.5] ((g5 g#5)[=0.5] _[=1] g5[=2] / d#5[=4]) :: =1 >0.1 attT0.4 relT3.5 #0.4"
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

### Experimentation
#tracks["pycompose:taper"] = " c2 c2[=1] (g2/f2)[=1] :: >1.3 relT2.2 =2 #0.3"
#tracks["pycompose:skib"] = "b3 {x3} g3 a3 d3 {x3} (a4/b4)[>1] :: =0.5 #0.2 >0.2 relT2 attT0.1"
#tracks["brute:somebrut"] = "c3[=0 fxb1] f4 a3 g3 b4 :: #0.1 fxb0.24 fxa0.2 =16 >6 relT2 attT0.5"
#tracks["brute:argh"] = "_ {x16} _ _ _ g5 d5 c5 _ (f4/b4) :: =0.5 #0.3 fxb0.64 fxa0.44 >0.1 relT2.2"
#tracks["pycompose:zzzap"] = " (_[=0.5]/_[=1]) {} g5 {x3} f6 {x6} c5 {x3} eb5 {x3} c3 {x6} d6 {x3} d5 {x3} eb5 {x3} :: >0.6 =0.25 #0.2"

# Something cool coming up helpre 
tracks["SP_Roland808:drum"] = "mi16[=0 ofs0.2] bd6 sn4 bd6 ((sn4/mi22) sn6)[=0.25] bd4[=0.5] :: #0.4 =1 >1 ofs0 rate2.7"
tracks["pluck:riff"] = "g3 g4 {x16} c3 g4 {x16} f4 g4 {x16} eb3 g4 {x16}  :: >0.3 =0.25 #0.34 relT0.2 attT0.1"
tracks["elisin:organ"] = "d5[=0] c2 g2 f2 d5[=0] eb2 :: =8 >2 #0.2 relT2 attT0.1"
tracks["gentle:raw"] = "f2t[=2] f6:t[=6] f2t[=1 >1] f2t[=1] f8:t[=6]  :: #0.2 >4 =4 prt0.2 fxa0.32 fxb22.02 fx2.2 relT2"
#tracks["brute:riiiigh"] = "g3[=0] d3 {x16} _ {x32} g4[=0] c3 {x64} :: =0.125 >0.05 #0.1 lfoD0.2 lfoS0.02 relT0.2"

### Theseus
# Start with annoy/harmonics, bring in rhythm for singing 

# fmod 1/2 hashs different feels  
#tracks["pycompose:bassline"] = "g3 b3 b3 g3[#0] b3 b3 g3[#0] b3 g3 b3 b3 c4 b3 g3 a3 g3 {} g3 c4 c4 g3[#0] c4 c4 g3[#0] c4 g3 c4 c4 d4 c4 g3 b3 g3  :: =0.5 >0.6 #0.2 relT2.2 fmod2 fxf500 fxs0.2 fxa0.4 cutoff1300"

# 2/4 oct for raise
#tracks["brute:annoy"] = "g2 {x32} c3 {x32} g2 {x32} c3 {x32} :: >0.06 =0.25 relT0.4 #0.15"
#tracks["brute:annoy"] = "g4 {x32} c5 {x32} g4 {x32} c5 {x32} :: >0.06 =0.25 relT0.4 #0.15"
#tracks["eli:rhythm"] = " _[=0.75] g2[=0.25] g2[=0.5] g2[=0.5] {x4} _[=0.75] c2[=0.25] c2[=0.5] c2[=0.5] {x4} :: >0.06 #0.4 =1 relT0.8"
#tracks["brute:harmonics"] = " d4[>0.04] c3 {x16} g4 g3[>0.04] {x16} d4[>0.04] c3 {x16} b3 g3[>0.04] {x16} :: >0.2 =0.25 #0.05 fx8.02 relT2"

#tracks["SP_Roland808:drum5X"] = " (bd2/(bd2 bd2)[=0.25] bd2[=1.5]) sn3[ofs0.02]  :: =2 rate2 ofs0 #0.8"

# Some variety for the drums 
#tracks["SP_Roland808:drum5X"] = " (mi28/_/_/_)[=0 #0.3 rate1] (bd2 mi34[=0 ofs0.03]/(bd2 bd2)[=0.25] bd2[=0.5] bd2[=1]) sn3[ofs0.02]  :: =2 rate2 ofs0"

#tracks["SP_Roland808:drum5X"] = " (mi28/_)[=0 #0.3 rate1]  (bd2[=1] bd2[=1]/(bd2 bd2)[=0.25] bd2[=0.5] bd2[=1]) sn3[ofs0.02 =1] bd2[=1]  :: =2 rate2 ofs0"

# First note is also cool as high 
#tracks["elisin:roar"] = " (g5 g2)[=0 >8 cut800 #0.2] d4 d4[=4] c4[=4] g3 c4[=2] b3[=6] :: >8 =8 #0.25 cut450"

client.read_custom_synths()
#client.stop() #
# TODO: Seems to stop everything forever if you do it for the very last remaining sequencer 
# This is for now remedied by calling client.stop when it happens 
client.wipe_on_finish()
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
