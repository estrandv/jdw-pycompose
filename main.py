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

# Note on BUS: 16-127 are virtual buses; anything played there must be routed to bus 0
# to actually make sound. This is done by using the outBus of effects.
client = PublisherClient()
client.wipe_effects()

EffectChain(18).bandpass(20, 640.0, bpr=0.83333, bpnoise=0.00, sus=8.0).reverb(0, mix=0.1).send(client)
client.set_bpm(140)

mode1.sheet("hh1 sh4 hh3 _").all("=0.25 #3")
experimental.sheet("1 5l 1 3 (6/2/8/5) 1s 4s", 3, MAJOR).all("#0.1 lfoD0.5 lfoS0.4").tag("l:=2 >2").tag("s:=0.5 >0.7")


####

# TODO: This one is cool as hell
#drsix1.sheet("bd3[#8] sn7[=0.5] (bd4/bd6)[=0.5 #8 pan0.6 bus40]")
#warsaw.sheet("1 (12/7)[mono1] 3 4 (6/8)[mono1] 3 4 0", 4, MINOR).all("#0.1 prt0.27")
#################

#reed.sheet("4 8", 5, MAJOR).all("=3 >6 #0.5")
#guitar.sheet("1 1 2 2 1 1 (4/4/8/2) 4 _ 2 1 2 (4/0) 2 4 2", 4, MINOR).all(">0.15 =0.5 lfoS2.2 lfoD2.2 #2")
#warsaw.sheet("8 8 7 8 9 9 7 (6/_)", 1, MINOR).all("#0.5 mono1 prt0.8 >1.2")
#drsix1.sheet("bd9 sh0[=0.25 #0.5] sh0[=0.25] (sn0/sn1) sh2[=0.5]").all("=1.5 >4 bus30 #4")
#warsaw.sheet("0 1 0 3", 3, MINOR_PENTATONIC).all("#0.2 =2 >3")
#experimental.sheet("0 5 _ 6 (8/4/8/9) 1 _ 0", 4, MINOR_PENTATONIC)\
#    .all("=0.5 >2.6 lfoD0.4 lfoS5.8 bus16 wid0.42555 prt0.48 #0.3 pan-0.3")
#korger1.sheet("cy3[#2] _ _ _ _ _ _").all("bus0")
#borch.sheet("to1 sn3").all("#4 bus30 pan0.7")

############ SAM STUFF
#korger1.sheet("1(cy3/cy7) _ to3 _ to8 _ _ _").all("#6")#
#mode1.sheet("hh1 hh8[#0.3] hh2 (hh6/_) hh2 hh1 hh3 (hh3[#0.8]t hh3t hh3[#0.7]t hh3t/cy3)").all("#0.4 =0.25 >0.25").tag("t:=0.0625 >0.06")
#drsix1.sheet("bd3[#8] sn7[=1] (bd4/bd6)[=2 #1 pan0.6]")
#moog.sheet("(8/4/5/4) 2 8 2", 5, MINOR).all(">0.2 =0.5 pan-0.8 #0.5 chorus2.2")
#rhodes.sheet("0q 3[>4]q 5 1q 4[>0.2]q (7/9)", 3, MINOR).all("=8 >8 #2").tag("q:=0")
#reed.sheet("3 4 0 4", 4, MINOR).all("=2 >0.4")
#stockSaw.sheet("0 2 8 3", 3, MINOR).all("=4 >4.2 mono1 prt2.45 bus16 #1")
#############

cmp.smart_sync([korger1])

client.update_synths()

#client.nrt_record(to_synth_notes(guitar, "electricGuitar"), 140, "guitar.wav", "synth")
#client.nrt_record(to_sample_notes(mode1, "ModeAudio"), 140, "drums.wav", "sample")
#client.nrt_record(drsix1.to_nrt(), 180, "drsix.wav", "sample")
#client.nrt_record(drsix1.to_nrt(), 180, "drsix.wav", "sample")

#client.nrt_record(cmp.nrt_export("drsix1"), 160, "drsiz.wav", "sample")
#client.nrt_record(cmp.nrt_export("guitar1"), 160, "guitar.wav", "synth")
#client.nrt_record(cmp.nrt_export("warsaw1"), 160, "warsaw.wav", "synth")
#client.nrt_record(cmp.nrt_export("moog1"), 160, "moog.wav", "synth")

for note_set in cmp.export_all():
    client.queue(note_set)
