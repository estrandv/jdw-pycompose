from random import randint

from scales import *
from new_sheet import *
from new_meta_sheet import *
from new_composer import *
from note_export import *
from zmq_client import PublisherClient

cmp = Composer()
# Synths 
blipp = cmp.meta_sheet("blipp", "blipp1", to_sequencer_synth_notes)
moog = cmp.meta_sheet("moogBass", "moog1", to_sequencer_synth_notes)
warsaw = cmp.meta_sheet("warsawBass", "warsaw1", to_sequencer_synth_notes)
reed = cmp.meta_sheet("organReed", "reed1", to_sequencer_synth_notes)
guitar = cmp.meta_sheet("electricGuitar", "guitar1", to_sequencer_synth_notes)

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
client.add_effect([{"target": "effect_reverb", "args": {"inBus":20, "outBus": 0, "room": 0.3, "mix":0.35}}])
client.add_effect([{"target": "effect_reverb", "args": {"inBus": 40, "outBus": 0, "room": 0.9, "mix":0.8}}])

client.add_effect([{"target": "effect_distortion", "args": {"inBus": 44, "outBus": 20, "dist": 0.08}}])
client.add_effect([{"target": "effect_reverb", "args": {"inBus": 50, "outBus": 0, "room": 0.4, "mix":0.2}}])

client.add_effect([{"target": "effect_combDelay", "args": {"inBus": 16, "outBus":20, "echo": 0.55, "beat_dur": 0.2, "echotime": 0.4}}])

client.set_bpm(140)

blipp.pad(64.0)
warsaw.sheet("(2/4/5/5) 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0", 3, MAJOR).all("pan-0.5 =0.25 >1 #0.7")
moog.sheet("4 _ 2 3", 3, MAJOR).all("=4 >4 #0.7 pan0.5 bus20")
guitar.sheet("0[#0.7] 0 0[=0.25 #0.8] (4/1/2/3)[=0.75 muteSus5]", 4, MAJOR).all("pan-0.3 =0.5 pickPos0.12 openFreq380 bus44 #2 >4 muteSus2")
mode1.sheet("bd4[#0.8 =0.5] (bd4[=1]/bd4[=0.25 #2 bus0] bd4[=0.75]) hh3[=0.5] (sn1/hh4) sn2[=0.5] hh3[=0.5]").all("bus0 pan0.3")

cmp.smart_sync()

#client.update_synths()

#client.nrt_record(to_synth_notes(guitar, "electricGuitar"), 140, "guitar.wav", "synth")
#client.nrt_record(to_sample_notes(mode1, "ModeAudio"), 140, "drums.wav", "sample")
#client.nrt_record(drsix1.to_nrt(), 180, "drsix.wav", "sample")
#client.nrt_record(drsix1.to_nrt(), 180, "drsix.wav", "sample")

for note_set in cmp.export_all():
    client.queue(note_set)

