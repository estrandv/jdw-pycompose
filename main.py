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

####

# TODO: This one is cool as hell
#drsix1.sheet("bd3[#8] sn7[=0.5] (bd4/bd6)[=0.5 #8 pan0.6]").all("bus0 ofs0.03")
#drsix1.sheet("bd3[#1] sn7[=0.5] (bd4/bd6)[=0.5 #1 pan0.6]")
#warsaw.sheet("1 (12/7)[mono1] 3 4 (6/8)[mono1] 3 4 0", 4, MINOR).all("#0.7 prt0.27 bus20")
#################

############ SAM STUFF
#korger1.sheet("(cy3/cy7) _ _ _ _ _ _ _").all("#6")#
#mode1.sheet("hh1 hh8[#0.3] hh2 (hh6/_) hh2 hh1 hh3 (hh3[#0.8]t hh3t hh3[#0.7]t hh3t/cy3)").all("#0.4 =0.25 >0.25").tag("t:=0.0625 >0.06")
#drsix1.sheet("bd3[#8] sn7[=1] (bd4/bd6)[=2 #1 pan0.6]")
#moog.sheet("(8/4/5/4) 2 8 2", 5, MINOR).all(">0.2 =0.5 pan-0.8 #0.5 chorus2.2 bus20")
#rhodes.sheet("0q 3[>4]q 5 1q 4[>0.2]q (7/9)", 3, MINOR).all("=8 >8 #1 bus20").tag("q:=0")
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
client.queue([note for notes in cmp.export_all() for note in notes])
