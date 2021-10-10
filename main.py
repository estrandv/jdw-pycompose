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
stockSine = cmp.meta_sheet("stockSine", "ssi1", to_sequencer_synth_notes)
rhodes = cmp.meta_sheet("FMRhodes1", "fm1", to_sequencer_synth_notes)
experimental = cmp.meta_sheet("experimental", "ex1", to_sequencer_synth_notes)
sinepad = cmp.meta_sheet("sinepad", "sp1", to_sequencer_synth_notes)

# Samplers
#modeAudio = cmp.reg(MetaSheet("modeAudio1", "ModeAudio", PostingTypes.SAMPLE, False))
korger1 = cmp.meta_sheet("KORGER1Samples", "korg1", to_sequencer_sample_notes)
drsix1 = cmp.meta_sheet("DR660", "drsix1", to_sequencer_sample_notes)
mode1 = cmp.meta_sheet("ModeAudio", "mode1", to_sequencer_sample_notes)
mode2 = cmp.meta_sheet("ModeAudio", "mode2", to_sequencer_sample_notes)
borch = cmp.meta_sheet("borch_sample", "borch1", to_sequencer_sample_notes)
tr808 = cmp.meta_sheet("TR808", "8081", to_sequencer_sample_notes)

# MIDI 
shaun = cmp.meta_sheet("BorchBattery", "shaun1", to_sequencer_midi_notes)
nintendo = cmp.meta_sheet("nintendo_soundfont", "nin1", to_sequencer_midi_notes)

# Note on BUS: 16-127 are virtual buses; anything played there must be routed to bus 0
# to actually make sound. This is done by using the outBus of effects.
client = PublisherClient()

client.set_bpm(120)

EffectChain(20).reverb("rev20", 0).debug().send(client)


#warsaw.pad(16.0).sheet("4 4 4 (2/4/6/2)", 3, MAJOR_PENTATONIC).all("#0.02 =0.5 >0.1 relT3 bus60 pan-0.15")

# 8 + 4 + 6*4=24 + 4 = 40 -> 64 = 24 / 4 = 

#mode1.sheet("to1 hh1[rate1.2] bd5 sn22").stretch(2).extend("to1 sn22[||=0.25 start50] sn22[||=0.25 #0.8] hh8[=0.5 #0.5] bd5 hh7")\
#    .all("bus0")
#warsaw.sheet("0 2 4 0", 2, MINOR).stretch(14).extend("6 6 6 6").all("bus30 #1 =0.25 >0.2")
#stockSine.sheet("_ _ _ _ 2 3 2[||=0.5 >0.5] 3 2 3 5 (6/2/4/8)[||=1.5 >1.5 #0.5] _ _ _ _", 3, MINOR_PENTATONIC)\
#    .extend("4[=16 >16 lfoS36.6]")\
#    .all("lfoD1 lfoS22.2 #0.2 bus60 >0.2")\
#    .shape([1,0], "lfoS", 7.4)
#stockSaw.pad(32.0).sheet("0 4 0 (4/2) 0 6 0 8", 5, MINOR).all("=0.5 >0.4 #0.03 bus30").stretch(3)
#korger1.sheet("0[#0 =31] be8[bus70 #0.2]")
#drsix1.sheet("0[#0 =63] mi48[bus30]")
#moog.sheet("2 4 6 4", 2, MINOR).all("=4 >5 bus20").shape([1,1,0,1], "time", 0.125)
#drsix1.sheet("bd10[start400 attT0.] sn0[start800]").stretch(6).extend("bd11 sn0[=0.25] sn0[=0.25||#0.6] hh8[=0.5]").all("#3 bus0").shape([1,0,0,1], "time", 0.021)
#drsix1.sheet("bd10 sn0 bd10 sn2").all("=0.5")
#mode1.sheet("bd4 sn4").all("=0.5")

#stockSaw.sheet("(3/5/2/1)[=0 >2 relT0.4 attT0.1 #0.3 lfoD0.8 lfoS440.0] 0[#0.2 =0.5] 0[pan-0.4] (0/2/0/1)[#0.8 =1.5] _", 4, MINOR)\
#    .all(">0.1 relT0.2 lfoD0.3 lfoS0.5 bus0")
#moog.sheet("0 (3/5/2/1) 0 (3/5/2/1) 0 (3/5/2/1) 0 (3/5/2/1)", 4, MINOR).all("=0.5 >0.3 #0.2 relT0.3 attT0.1 bus20").shape([1,0,1,1,0,0], "sus", 0.73)
#warsaw.sheet("0 _", 2, MINOR).all("=0.5 >0.1 #0.2")
#moog.sheet("(8/6/4/5) 12 (9/10) _", 3, MINOR_PENTATONIC).all("=0.5 >0.3 relT0.5 #0.4")

### TODO: Also pretty cool

korger1.sheet("cy4[=16 ofs0.0 bus0]")
mode1.sheet("to1 to2").all("=0.125 bus20 ofs0.03").shape([1,0], "amp", 0.5)
warsaw.sheet("0 0[=0.5] (0/2) 0 0 0[=0.5]", 2, MINOR_PENTATONIC).all(">0.1 =0.25 #0.6")
moog.sheet("0 3 1 3 (2/7/5/9) 1 4 1", 4, MINOR_PENTATONIC).all("=0.5 >0.6 mono1 prt0.08 bus0 pan-0.2")
stockSaw.sheet("0 0[=0.5] 0 (4/6) 1 0 1[=0.5] 0 0", 5, MINOR).all(">1.1 mono1 prt0.3 lfoS2.2 lfoD0.2 pan0.2 bus20 #0.2")
drsix1.sheet("bd3 sn2 bd1[||=0.5] bd1[||=0.5] sn2[||=0.5] bd1[||=0.5]")\
    .stretch(2)\
    .extend("bd3 sn2 hh1[||=0.25] hh5[||=0.5] hh4[||=1.25]")\
    .shape([0,1], "amp", 0.08).all("ofs0.00 bus20")#.shape([1,1,0], "ofs", 0.005)

####

# TODO: This one is cool as hell
#drsix1.sheet("bd3[#8] sn7[=0.5] (bd4/bd6)[=0.5 #8 pan0.6]").all("bus30")
#drsix1.sheet("bd3[#1] sn7[=0.5] (bd4/bd6)[=0.5 #1 pan0.6]")
#warsaw.sheet("1 (12/7)[mono1] 3 4 (6/8)[mono1] 3 4 0", 4, MINOR).all("#0.1 prt0.27 bus0")
#################

#reed.sheet("4 8", 5, MAJOR).all("=3 >6 #0.5")
#guitar.sheet("1 1 2 2 1 1 (4/4/8/2) 4 _ 2 1 2 (4/0) 2 4 2", 4, MINOR).all(">0.15 =0.5 lfoS2.2 lfoD2.2 #2 bus0").shape([1,0,1,1,0,0], "time", 0.08)
#warsaw.sheet("8 8 7 8 9 9 7 (6/_)", 1, MINOR).all("#0.5 mono1 prt0.8 >1.2")
#drsix1.sheet("bd9 sh0[=0.25 #0.5] sh0[=0.25] (sn0/sn1) sh2[=0.5]").all("=1.5 >4 bus30 #4")
#warsaw.sheet("0 1 0 3", 3, MINOR_PENTATONIC).all("#0.2 =2 >3 bus20")
#experimental.sheet("0 5 _ 6 (8/4/8/9) 1 _ 0", 4, MINOR_PENTATONIC)\
#    .all("=0.5 >2.6 lfoD0.4 lfoS5.8 bus16 wid0.42555 prt0.48 #0.3 pan-0.3")
#korger1.sheet("cy3[#2] _ _ _ _ _ _").all("bus0")
#borch.sheet("to1 sn3").all("#1 pan0.7")

############ SAM STUFF
#korger1.sheet("1(cy3/cy7) _ to3 _ to8 _ _ _").all("#6")#
#mode1.sheet("hh1 hh8[#0.3] hh2 (hh6/_) hh2 hh1 hh3 (hh3[#0.8]t hh3t hh3[#0.7]t hh3t/cy3)").all("#0.4 =0.25 >0.25").tag("t:=0.0625 >0.06")
#drsix1.sheet("bd3[#8] sn7[=1] (bd4/bd6)[=2 #1 pan0.6]")
#moog.sheet("(8/4/5/4) 2 8 2", 5, MINOR).all(">0.2 =0.5 pan-0.8 #0.5 chorus2.2 bus20")
#rhodes.sheet("0q 3[>4]q 5 1q 4[>0.2]q (7/9)", 3, MINOR).all("=8 >8 #1 bus20").tag("q:=0")
#reed.sheet("3 4 0 4", 4, MINOR).all("=2 >0.4")
#stockSaw.sheet("0 2 8 3", 3, MINOR).all("=4 >4.2 mono1 prt2.45 bus20 #1 hpf200 lpf300")
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

for note_set in cmp.export_all():
    client.queue(note_set)
