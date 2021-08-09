from random import randint

from scales import *
from new_sheet import *
from new_meta_sheet import *
from new_composer import *
from note_export import *
from zmq_client import PublisherClient
from time import sleep

cmp = Composer()
# Synths 
blipp = cmp.meta_sheet("blipp", "blipp1", to_sequencer_synth_notes)
moog = cmp.meta_sheet("moogBass", "moog1", to_sequencer_synth_notes)
warsaw = cmp.meta_sheet("warsawBass", "warsaw1", to_sequencer_synth_notes)
reed = cmp.meta_sheet("organReed", "reed1", to_sequencer_synth_notes)
guitar = cmp.meta_sheet("electricGuitar", "guitar1", to_sequencer_synth_notes)
stockSaw = cmp.meta_sheet("stockSaw", "ss1", to_sequencer_synth_notes)
rhodes = cmp.meta_sheet("FMRhodes1", "fm1", to_sequencer_synth_notes)

# Samplers
#modeAudio = cmp.reg(MetaSheet("modeAudio1", "ModeAudio", PostingTypes.SAMPLE, False)) 
korger1 = cmp.meta_sheet("KORGER1Samples", "korg1", to_sequencer_sample_notes)
drsix1 = cmp.meta_sheet("DR660", "drsix1", to_sequencer_sample_notes)
mode1 = cmp.meta_sheet("ModeAudio", "mode1", to_sequencer_sample_notes)
mode2 = cmp.meta_sheet("ModeAudio", "mode2", to_sequencer_sample_notes)
borch = cmp.meta_sheet("borch_sample", "borch1", to_sequencer_sample_notes)
#blipp2 = cmp.reg(MetaSheet("bass_assist", "blipp", PostingTypes.PROSC))
#warsaw = cmp.reg(MetaSheet("warsaw", "warsawBass", PostingTypes.PROSC))
#warsaw2 = cmp.reg(MetaSheet("warsaw2", "warsawBass", PostingTypes.PROSC))
#moog = cmp.reg(MetaSheet("moog", "moogBass", PostingTypes.PROSC))
#moog2 = cmp.reg(MetaSheet("moog2", "moogBass", PostingTypes.PROSC))
#organReed = cmp.reg(MetaSheet("organReed1", "organReed", PostingTypes.PROSC))
#chaoscillator = cmp.reg(MetaSheet("chaos1", "chaoscillator", PostingTypes.PROSC))
#yamaha = cmp.reg(MetaSheet("yamaha", "YHDX200", PostingTypes.SAMPLE, False))
#yamaha2 = cmp.reg(MetaSheet("yamaha2", "YHDX200", PostingTypes.SAMPLE, False))
#korger = cmp.reg(MetaSheet("korger", "KORGER1Samples", PostingTypes.SAMPLE, False))
#korger2 = cmp.reg(MetaSheet("korger2", "KORGER1Samples", PostingTypes.SAMPLE, False))
#simple_korg = cmp.reg(MetaSheet("simple_korg", "KORGER1", PostingTypes.SAMPLE, False))
#longsaw = cmp.reg(MetaSheet("longsaw", "longsaw", PostingTypes.PROSC))
#longsaw2 = cmp.reg(MetaSheet("longsaw2", "longsaw", PostingTypes.PROSC))
#varsaw = cmp.reg(MetaSheet("varsaw1", "varsaw", PostingTypes.PROSC))
#varsaw2 = cmp.reg(MetaSheet("varsaw2", "varsaw", PostingTypes.PROSC))
#sinepad = cmp.reg(MetaSheet("sinepad1", "sinepad", PostingTypes.PROSC))
#rhodes = cmp.reg(MetaSheet("FMRhodes1", "FMRhodes1", PostingTypes.PROSC))
#borch = cmp.reg(MetaSheet("BorchBattery", "BorchBattery", PostingTypes.MIDI, False))
#drsix = cmp.reg(MetaSheet("drsix", "DR660", PostingTypes.SAMPLE, False))
#nintendo = cmp.reg(MetaSheet("nintendo_soundfont1", "nintendo_soundfont", PostingTypes.MIDI, False))
#nintendo2 = cmp.reg(MetaSheet("nintendo_soundfont2", "nintendo_soundfont", PostingTypes.MIDI, False))
#xtndo = cmp.reg(MetaSheet("xtndo1", "xtndo", PostingTypes.SAMPLE, False))
#modeAudio = cmp.reg(MetaSheet("modeAudio1", "ModeAudio", PostingTypes.SAMPLE, False))
#simpleKick = cmp.reg(MetaSheet("simpleKick1", "simpleKick", PostingTypes.PROSC))
# lfomul, hpf, lfow, pan
#modulOSC = cmp.reg(MetaSheet("mosc1", "modulOSC", PostingTypes.PROSC))
# attT, susL, decT, relT, hpf, lpf 
#stockSaw = cmp.reg(MetaSheet("ssaw1", "stockSaw", PostingTypes.PROSC))
#stockSaw2 = cmp.reg(MetaSheet("ssaw2", "stockSaw", PostingTypes.PROSC))
#stockSquare = cmp.reg(MetaSheet("ssquare1", "stockSquare", PostingTypes.PROSC))
#stockSine = cmp.reg(MetaSheet("ssine1", "stockSine", PostingTypes.PROSC))

# Note on BUS: 16-127 are virtual buses; anything played there must be routed to bus 0 
# to actually make sound. This is done by using the outBus of effects. 
# TODO: EffectChain object for simplifying: chain.add("effect_distortion","dist0.08", 66).reverb("room0.3 mix0.3", 0)
client = PublisherClient()
client.add_effect([{"target": "effect_reverb", "args": {"inBus":20, "outBus": 0, "room": 0.8, "mix":0.35}}])
client.add_effect([{"target": "effect_reverb", "args": {"inBus": 40, "outBus": 0, "room": 0.9, "mix":0.8}}])
client.add_effect([{"target": "effect_reverb", "args": {"inBus": 50, "outBus": 0, "room": 0.4, "mix":0.2}}])
client.add_effect([{"target": "effect_distortion", "args": {"inBus": 44, "outBus": 40, "dist": 0.018}}])

client.add_effect([{"target": "effect_combDelay", "args": {"inBus": 16, "outBus":20, "echo": 0.55, "beat_dur": 0.2, "echotime": 0.4}}])
client.add_effect([{"target": "effect_combDelay", "args": {"inBus": 34, "outBus":40, "echo": 0.03, "beat_dur": 0.01, "echotime": 8.4}}])

client.set_bpm(120)

# Beats number increases each tick 
# if number is more than 1/24, a sync is sent and remainder saved
# 

#blipp.pad(64.0)
#warsaw.sheet("(1/2/3/4) 0 0g 0 0 0g 0 0 | 0 0g 0 0 0g 0 0 0", 2, MAJOR)\
#    .all("pan0.3 =0.5 >2.5 susL0.6 #0.7 width0.4 bus20 slideTime0.04 cutoff1200 dec0.4 rel0")\
#    .tag("g:#0.3 cutoff600 rel2 width0.3 susL1.5 slideTime0.4 pan-0.1 bus16")
#stockSaw.sheet("6[=1.5] 2[=0.5] _ _ 6[=1.5] (2/7/0/5) 3[=1.5]", 5, MINOR).all("=1 bus44 pan0.0 lfoD2 lfoS0.1 lpf800 #0.4")
#guitar.sheet("8[=0.25 >2] (8/2/4/2)[=0.25] 0 0 0 0 0[=0.25] 0[=0.25] 0 0", 3, MINOR).all("=0.5 >1.3 #1.4 pan0.2 bus20")
#moog.sheet("7[=0 #0.4 >6 chorus0.4 pan0.7] 4 _ 2 (3/0)", 3, MAJOR).all("=4 >4 #0.8 pan0.4 bus40")
#reed.sheet("(0/7) _ (1/3) (2/1)", 5, MAJOR).all("=4 >4 #1.2 pan0.4 bus44 lfoD2 lfoS2")
#guitar.sheet("0[#0.7] 0 0[=0.25 #0.8] (4/1/2/3)[=0.75 muteSus5]", 4, MAJOR).all("pan-0.3 =0.5 pickPos0.12 openFreq380 bus44 #2 >4 muteSus2")
#mode1.sheet("bd4[#0.8 =0.5] (bd4[=1]/bd4[=0.25 #2 bus0] bd4[=0.75]) hh3[=0.5] (sn1/hh4) sn2[=0.5] hh3[=0.5]").all("bus0 pan0.3")

#reed.sheet("2 4 2 0", 5, MINOR).all("=4 >4 pan-0.4")
#stockSaw.sheet("0 1 1 2 1 1 3 1 1 0 1 1", 3, MINOR).all("pan0.5 >0.25 bus20 lfoD0.4 lfoS0.2 #2")
#rhodes.sheet("3 4 4 5 3 3 6 4 4 3 4 4", 5, MINOR).all("pan0.5 >0.25 bus20 lfoD0.4 lfoS0.2 #2")
#warsaw.sheet("0 0 0 (2/4)", 1, MINOR).all(">2")


# TODO: This one is cool as hell 
drsix1.sheet("bd3[#8] sn7[=0.5] (bd4/bd6)[=0.5 #4]")
stockSaw.sheet("1 (12/7)[mono1] 3 4 (6/8)[mono1] 3 4 0", 4, MINOR).all("#0.5 prt0.27")

#warsaw.sheet("0[=0.2 >2] 44[=11.8 >12 mono1] 2[=16 >8 mono1]", 2, MINOR).all("prt2.2")
#moog.sheet("0 2 (4/3)[mono1] (2/0)", 4, MINOR).all("=4 >4.2 #0.4 fx0.2 pan0.3 prt0.28")
#moog.sheet("0 (0/1[=0.5] 1[=0.5]) 4 8 0 0 8 6[=0.5] 9[=0.5 >0.25]", 4, MINOR)

#korger1.sheet("cy1 to3 to2 to4")

#korger1.sheet("cy1")

# Rhythm: [1, 0.5, 1, 0.5, 1, 0.5, 1, 0.5, 0.25, 0.75]
# .arg("time", [1, 0.5, 1, 0.5, 1, 0.5, 1, 0.5, 0.25, 0.75])
# Problems: 
#   ()-usage can lead to confusing setups 
#drsix1.sheet("bd3[#8] sn0[pan0.056 =0.5 rate1.1] bd20[=1 #4] bd3[=0.5 #7] (sn0[pan-0.045]/sn0[pan-0.5 =0.25 #0.9] bd3[#8 =0.75])") \
#   .all("bus20")
#stockSaw.sheet("4 3 2 0 (4 3 5 3/2[=4 >2] 0 1)", 5, MAJOR).all("=2 >1 relT1 attT0.1 hpf2000 bus20")
#borch.sheet("to2 sn4")
#moog.sheet("(0/4)[=8 >0.5 #0.5]", 3, MINOR)
#stockSaw.sheet("(8/12/4/5) _ _ 8 9 9 _ 9 9 9 4 _", 3, MINOR).all("lpf1200 lfoD2 lfoS0.5 bus20 relT2 =0.5")
#drsix1.sheet("bd20")
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
