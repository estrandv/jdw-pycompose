from random import randint

from scales import *
from new_sheet import *
from new_meta_sheet import *
from new_composer import *
from note_export import *
from zmq_client import PublisherClient

cmp = Composer()
#padder = cmp.reg(MetaSheet("padder", "blipp", PostingTypes.PROSC))
blipp = cmp.meta_sheet("blipp", "blipp1", to_sequencer_synth_notes)
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
#borchBattery = cmp.reg(MetaSheet("borch1", "borch_sample", PostingTypes.SAMPLE, False))
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
client = PublisherClient()
client.add_effect([{"target": "effect_reverb", "args": {"inBus":20, "outBus": 0, "room": 0.4, "mix":0.4}}])
client.add_effect([{"target": "effect_reverb", "args": {"inBus": 40, "outBus": 0, "room": 0.9, "mix":0.8}}])

client.add_effect([{"target": "effect_distortion", "args": {"inBus": 44, "outBus": 0, "dist": 0.08}}])
client.add_effect([{"target": "effect_reverb", "args": {"inBus": 50, "outBus": 0, "room": 0.4, "mix":0.2}}])

client.add_effect([{"target": "effect_combDelay", "args": {"inBus": 16, "outBus":40, "echo": 0.55, "beat_dur": 0.2, "echotime": 0.4}}])

client.set_bpm(180)

cmp.pre_tag("t:=.25").pre_tag("s:=.5").pre_tag("q:=0").pre_tag("l:=2 >2").pre_tag("xl:=4 >5").pre_tag("_:#0")



#client.nrt_record(drsix.to_nrt(), 180, "test_emil.wav", "sample")

#cmp.post_all()

