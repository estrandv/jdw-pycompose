from random import randint

from scales import *
from new_sheet import *
from new_meta_sheet import *
from new_composer import *
from note_export import *
from zmq_client import PublisherClient
from time import sleep
from effects import EffectChain
import time

cmp = Composer()
# Synths
blipp = cmp.meta_sheet("blipp", "blipp1", to_sequencer_synth_notes)
moog = cmp.meta_sheet("moogBass", "moog1", to_sequencer_synth_notes)
warsaw = cmp.meta_sheet("warsawBass", "warsaw1", to_sequencer_synth_notes)
reed = cmp.meta_sheet("organReed", "reed1", to_sequencer_synth_notes)
guitar = cmp.meta_sheet("electricGuitar", "guitar1", to_sequencer_synth_notes)
stockSaw = cmp.meta_sheet("stockSaw", "ss1", to_sequencer_synth_notes)
stockSaw2 = cmp.meta_sheet("stockSaw", "ss2", to_sequencer_synth_notes)
stockSquare = cmp.meta_sheet("stockSquare", "sq1", to_sequencer_synth_notes)
stockSine = cmp.meta_sheet("stockSine", "ssi1", to_sequencer_synth_notes)
rhodes = cmp.meta_sheet("FMRhodes1", "fm1", to_sequencer_synth_notes)
experimental = cmp.meta_sheet("experimental", "ex1", to_sequencer_synth_notes)
sinepad = cmp.meta_sheet("sinepad", "sp1", to_sequencer_synth_notes)
miniBrute = cmp.meta_sheet("miniBrute", "mb1", to_sequencer_synth_notes)
miniBrute2 = cmp.meta_sheet("miniBrute", "mb2", to_sequencer_synth_notes)

# Samplers
#modeAudio = cmp.reg(MetaSheet("modeAudio1", "ModeAudio", PostingTypes.SAMPLE, False))
korger1 = cmp.meta_sheet("KORGER1Samples", "korg1", to_sequencer_sample_notes)
drsix1 = cmp.meta_sheet("DR660", "drsix1", to_sequencer_sample_notes)
mode1 = cmp.meta_sheet("ModeAudio", "mode1", to_sequencer_sample_notes)
mode2 = cmp.meta_sheet("ModeAudio", "mode2", to_sequencer_sample_notes)
example = cmp.meta_sheet("example", "ex1", to_sequencer_sample_notes)
# Indactive
#borch = cmp.meta_sheet("borch_sample", "borch1", to_sequencer_sample_notes)
# Inactive
#tr808 = cmp.meta_sheet("TR808", "8081", to_sequencer_sample_notes)

# MIDI 
shaun = cmp.meta_sheet("BorchBattery", "shaun1", to_sequencer_midi_notes)
nintendo = cmp.meta_sheet("nintendo_soundfont", "nin1", to_sequencer_midi_notes)

# Note on BUS: 16-127 are virtual buses; anything played there must be routed to bus 0
# to actually make sound. This is done by using the outBus of effects.
client = PublisherClient()

bpm = 110
client.set_bpm(bpm)

# TODO: Effects need tweaking:
# - Adding again appears to cause multi-layer and distortion (is dist misprogrammed?)
# - Removing with comment doesn't remove effect 
# - Should work with argparse 

client.set_effects([
    ["effect_reverb", "in20 out0 room0.8 mix0.4"],
    ["effect_nhall", "in30 out0 hi4000 low800 edi0.4 ldi0.7 dec2"]
])

####

#miniBrute.sheet("5 7 (8/6/9/5) 7", 3, MINOR_PENTATONIC)\
#    .all(">0.4 relT0.2 fca2 lpf800 fcp0.2 ace0.8 fcd0.1 fcs0.4 sqr0.2 sne0.05 saw0.8 fcr0.2 bus30 lfoS120.8 lfoD0.1")
#miniBrute2.sheet("8 9 9 7 9 9 (8/2/9/0)[relT8 sne0.8] 8", 3, MINOR)\
#    .all("relT4 fcr4 fca2 fcp0.7 fcs1 lfoS9.95 lfD0.2 ace1.4 hpf1800 #0.2 >0.4 =1 bus0 sne0.2 saw1.0 sqr0.2")

#miniBrute.sheet("(3/6)[>0.4] (10/_/2/1)", 3, MINOR).all("=0.25 >0.05 #0.4")
#mode1.sheet("0")

# TODO: Considering changes to code/parsing
example_string = "*3 | 0 1 _ 4t (5/_/7/0) 2 3 1 | <all> =0.5 <t> fx0.99"

#mode1.sheet("bd0 1 sn2 33")
miniBrute.sheet("0 1 _ 4 (5/_/7/0) 2 3 1", 3, MINOR_PENTATONIC)\
    .all(">0.1 relT0.2 =0.25 fx0.99 bus0 lfoD0.24 lfoS0.01")
#stockSquare.sheet("0[||=0.5] 0[||=0.25] 1[||=0.25] (3[=2]/3[=2 >3]) (4/1/3/2) _ _ _ _", 3, MINOR_PENTATONIC).all(">0.1 bus20 rel0.2 #0.5 mono1 prt0.4")
#korger1.sheet("bd1[ofs0.02] bd4[=2] bd1[=2]").all("=4 #0.8")
#warsaw.sheet("0 _ 0 0 0 _ 0 (2/3)", 2, MINOR_PENTATONIC).all("attT0.1 =0.25 relT0.1 bus30 #0.1")
#sinepad.sheet("8[fmod11] 10[fmod10 blur0.76] 7[fmod13] 5[fmod4]", 4, MINOR_PENTATONIC).all("pan-0.1 =8 >12 #0.14 bus20")
#miniBrute.sheet("(0/2/3/5) 6 _ 7", 4, MINOR_PENTATONIC)\
#    .all("lfoS0.005 lfoD0.5 >0.1 =1 relT2.5 fx0.02 #0.5 fcx0 bus20 ace2 hpf4400 pan0.1")

#### Rainday

#mode1.sheet("bd2[osf0.04] sn4 bd2[=0.25 ofs0] bd2[=0.75 ofs0.1] sn4").all("bus0 #0.6")
#mode1.sheet("hh1[=2.75 ofs0.07] (mi2/mi3)[=1.25 ofs0.38]")
#drsix1.sheet("hh1[=0.25] hh2 hh1[=0.75] (cy4/cy4/cy4/cy3)[=0 >2] hh3[=2]").all("#0.7")

#blipp.sheet("1[=0 >16] 4[=0 >16] 0 2 3[=3] (8/7)[=5]", 5, MAJOR_PENTATONIC).all("=4 >4 #0.07")
#stockSaw.sheet("0 0 0 0 0 0 0 (5/8/2/1)", 2, MAJOR_PENTATONIC).all(">0.05 =0.25 fx0.2 #1")
#warsaw.sheet("0 7 3 0", 5, MINOR_PENTATONIC).all("mono1 >8 =8 #0.03 prt2")
#drsix1.sheet("bd2[ofs0] sn0 bd2[=0.5] bd2[=0.5 ofs0] sn0[=0.5 ofs0.05] bd2[=0.5 ofs0.08]").all("#0.8")

#rhodes.sheet("9 8 8 7 8 8 9 (4/3)", 5, MAJOR).all(">0.4 =2 lfoS2 lfoD0.2")
#warsaw.sheet("0 (1/2/3/4/3/4/0/0)", 4, MINOR_PENTATONIC).all(">2 =0.5 bus30 #0.25 mono1")
#drsix1.sheet("mi25[=32] bus20")

#miniBrute2.sheet("0 2 3 (4/8/2/12)", 3, MAJOR_PENTATONIC).all(">0.2 relT1 cut0 ace2 lfoS1.05 lfoD0.1 =0.5 attT0.1")
#miniBrute.sheet("10[=0 lfoS0.1 lfoD0.2 >2] 0 1 3 4", 3, MAJOR_PENTATONIC).all(">0.5 attT0.1 lfoS2.2 lfoD0.04 relT0.8 susL0.8 bus20")
#miniBrute.sheet("(0/4/1/5)[cut1 ace4 lfoS444 lfoD0.8 relT5] 2 3 2", 3, MAJOR).all("bus20 #0.23 >0.5 lfoS44.2 relT2 susL0.8 decT0.2 attT0.1 lfoD0.04 =1")
#miniBrute2.sheet("(0/4/1/5)[fcs4 fcr4 fcd0.5 fca0.5 lfoS444 lfoD0.8 relT5] 2 (5/3/4/3) 2", 4, MAJOR)\
#    .all("#0.23 >0.5 lfoS44.2 relT2 susL0.8 decT0.2 attT0.1 lfoD0.04 bus30 =1")
#miniBrute.sheet("0 0 0 2", 3, MINOR_PENTATONIC).all("relT4 >0.1 attT0.08 =1 #0.4 attT0 relT4 fcr2 fca0.05 fcs2 lfoS440 lfoD0.4")
#####


#example.sheet("1 2").all("#2 =0.5")
#miniBrute2.sheet("4 2 4[>0.5 =2] 2 (3/0)[lfoS0.2 lfoD0.3 >2]", 4, MINOR).all("#0.10 >0.2 =0.30")


#drsix1.sheet("sh3 sh4[ofs0.12]").all("=0.125 bus20").shape([1,0], "time", 0.08)
#mode1.sheet("bd5 hh3 bd5[=0.5] bd5[=0.5] hh3").all("ofs0.03")
#example.sheet("1[ofs0] 2 1 2[pan-0.2] 1 2[pan0.2] 1 1[=0 ofs0] 3s 3[ofs0.02]s 3t").tag("s:=0.25 ofs0").tag("t:=0.5")
#example.sheet("1 2 1[=0.25] 1[=0.75 ofs0.02] 2[=0.5] 3[=0.5 >4]").all("#3 ofs0 pan-0.2")
#miniBrute.sheet("2 (2/0) 5 (4/1/6/2/3/6/1/2)", 4, MINOR_PENTATONIC).all(">0.1 =0.25 relT0.1 fx6.6 susL0.2 pan0.2 #0.8")
#miniBrute2.sheet("(5/5[relT4 fx0.85 lfoS20.62 lfoD0.2]) (3/1) (5/5/9/6) 0", 3, MINOR_PENTATONIC).all(">0.2 =0.5 relT1.6 fx0.6 susL0.2 pan0.25 #0.4")
#miniBrute.sheet("0 0 0 (2/1/3/4)", 2, MINOR_PENTATONIC).all(">1 =2 #0.13")

#miniBrute.sheet("8 8 (9/11)[=7] 9 8 (12/5)[=7]", 3, MINOR_PENTATONIC).all(">0.05 relT4 bus0 lfoS222.21 lfoD0.45 =0.5 #0.7")
#miniBrute2.sheet("0[=0 >3] 1[=0 >2] 12[=0 lfoS440 lfoD0.05] (4/6/4/5)[=8 relT4]", 2, MAJOR_PENTATONIC).all(">4 #0.15 bus30 lfoS0.125 lfoD0.4 attT0.1")
#warsaw.sheet("0s 0s 2 1 3 5s 5s 0 3 (7/2)", 3, MINOR_PENTATONIC).all("bus20 >0.1 #0.25 =0.5").tag("s:=0.25")

####
#guitar.sheet("0 2 0 18 0 (2/14/8/3)[>0.2] 0 2", 4, MINOR_PENTATONIC).all("#0.5 >0.02 =0.5 fx0.3 bus0")
#guitar.sheet("4 6 8 9", 4, MINOR_PENTATONIC).all("#0.1 >12 =8 fx0.3 bus80")
#mode1.sheet("bd0 sn0").all("ofs0 bus0 #0.76")
#drsix1.sheet("cy5 _ _ _ _ _ _").all("bus0 =2 ofs0.22 #0.2")
#rhodes.sheet("0 0 2 3 3 2 4 4 (2/0) _ _ _ _ _ _ _", 4, MINOR_PENTATONIC).all("lfoD0.4 lfoS4 bus0 #2")
#korger1.sheet("_ _ _ mi9").all("bus0 #0.6")
#borch.sheet("to0 sn0[=0.5] to1[=1.5] (sn2/mi12[ofs0.02]/sn2/sn2)").all("ofs0.0 bus0")
#moog.sheet("(2/2/4/4) (2/2/4/4) (2/2/4/4) (3/0/0/12)", 3, MINOR_PENTATONIC).all("fx0.4 mono1 bus0 prt0.27 lfoS8 lfoD0.2 #0.6")
#warsaw.sheet("0[=2] 0[=0.5] 0[=0.5] 0", 2, MINOR_PENTATONIC).all(">0.5 bus0 lfoS4 lfoD0.5 #0.2")
#experimental.sheet("0 0 0 (1/2/5/0)", 4, MINOR_PENTATONIC).all(">0.4 #0.1")


# TODO: This one is cool as hell
#korger1.sheet("bd3 sn2 bd3[=0.25 ofs0.03] bd3[=0.75] (sn2[ofs0.03]/sn2[ofs0.04 =0.5] be4[=0.5])")

#drsix1.sheet("bd3[#8] sn7[=0.5] (bd4/bd6)[=0.5 #8 pan0.6]").all("bus0 ofs0.03")
#drsix1.sheet("bd3[ofs0] sn2").all("#3")
#warsaw.sheet("2 3 2 3 2 4 2 (3/7/6/5)[>0.8]", 2, MINOR_PENTATONIC).all(">0.05 fx0.2 =0.25")
#korger1.sheet("mi3 hh4 _ be5").all("=0.25 ofs0 >0.1")
#mode1.sheet("be5[=16 #5 ofs0]")
#stockSaw.sheet("(7/5) 7[>1] _ 8 (6/7) (7/1) _ (8/2) _[=4]", 3, MINOR_PENTATONIC).all("=0.5 >0.25")
#reed.sheet("8[>1] _ 8 _ 8 8 _ 9 (5/4/2/5)[>0.5 =7 fx1]", 3, MINOR_PENTATONIC).all(">0.05 =0.125 #4")

#warsaw.sheet("1 (12/7)[mono1] 3 4 (6/8)[mono1] 3 4 0", 4, MINOR).all("#0.1 prt0.27 bus0").shape([1,0], "time", 0.05)
#################

############ SAM STUFF
#korger1.sheet("(cy3/cy7) _ _ _ _ _ _ _").all("#6")#
#mode1.sheet("hh1 hh8[#0.3] hh2 (hh6/_) hh2 hh1 hh3 (hh3[#0.8]t hh3t hh3[#0.7]t hh3t/cy3)").all("#0.4 =0.25 >0.25").tag("t:=0.0625 >0.06")
#drsix1.sheet("bd3[#8] sn7[=1] (bd4/bd6)[=2 #1 pan0.6]")
#moog.sheet("(8/4/5/4) 2 8 2", 5, MINOR).all(">0.2 =0.5 pan-0.8 #0.5 chorus2.2 bus20")
#rhodes.sheet("0q 3[>4]q 5 1q 4[>0.2]q (7/9)", 3, MINOR).all("=8 >8 #1 bus0").tag("q:=0")
#reed.sheet("3 4 0 4", 4, MINOR).all("=2 >0.4")
#stockSaw.sheet("0 2 8 3", 5, MINOR).all("=4 >4.2 mono1 prt2.45 bus0 #1 hpf200 lpf300")
#############

cmp.smart_sync()

client.update_synths()

#client.nrt_record(to_synth_notes(guitar, "electricGuitar"), 140, "guitar.wav", "synth")
#client.nrt_record(to_sample_notes(mode1, "ModeAudio"), 140, "drums.wav", "sample")
#client.nrt_record(drsix1.to_nrt(), 180, "drsix.wav", "sample")
#client.nrt_record(drsix1.to_nrt(), 180, "drsix.wav", "sample")

#client.nrt_record(cmp.nrt_export("drsix1"), 140, "drsiz.wav", "sample")
#client.nrt_record(cmp.nrt_export("warsaw1"), 140, "warsaw.wav", "synth")
#client.nrt_record(cmp.nrt_export("guitar1"), 160, "guitar.wav", "synth")
#client.nrt_record(cmp.nrt_export("warsaw1"), 160, "warsaw.wav", "synth")
#client.nrt_record(cmp.nrt_export("moog1"), 140, "moog.wav", "synth")

client.wipe(cmp.export_wipe_aliases())
#cmp.nrt_export_all(client, bpm)
client.queue([note for notes in cmp.export_all() for note in notes])
