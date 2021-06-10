from random import randint

from scales import *
from sheet import *
from zmq_client import PublisherClient

cmp = Composer()
padder = cmp.reg(MetaSheet("padder", "blipp", PostingTypes.PROSC))
blipp = cmp.reg(MetaSheet("bass", "blipp", PostingTypes.PROSC))
blipp2 = cmp.reg(MetaSheet("bass_assist", "blipp", PostingTypes.PROSC))
warsaw = cmp.reg(MetaSheet("warsaw", "warsawBass", PostingTypes.PROSC))
warsaw2 = cmp.reg(MetaSheet("warsaw2", "warsawBass", PostingTypes.PROSC))
moog = cmp.reg(MetaSheet("moog", "moogBass", PostingTypes.PROSC))
moog2 = cmp.reg(MetaSheet("moog2", "moogBass", PostingTypes.PROSC))
organReed = cmp.reg(MetaSheet("organReed1", "organReed", PostingTypes.PROSC))
chaoscillator = cmp.reg(MetaSheet("chaos1", "chaoscillator", PostingTypes.PROSC))
yamaha = cmp.reg(MetaSheet("yamaha", "YHDX200", PostingTypes.SAMPLE, False))
yamaha2 = cmp.reg(MetaSheet("yamaha2", "YHDX200", PostingTypes.SAMPLE, False))
korger = cmp.reg(MetaSheet("korger", "KORGER1Samples", PostingTypes.SAMPLE, False))
korger2 = cmp.reg(MetaSheet("korger2", "KORGER1Samples", PostingTypes.SAMPLE, False))
simple_korg = cmp.reg(MetaSheet("simple_korg", "KORGER1", PostingTypes.SAMPLE, False))
longsaw = cmp.reg(MetaSheet("longsaw", "longsaw", PostingTypes.PROSC))
longsaw2 = cmp.reg(MetaSheet("longsaw2", "longsaw", PostingTypes.PROSC))
varsaw = cmp.reg(MetaSheet("varsaw1", "varsaw", PostingTypes.PROSC))
varsaw2 = cmp.reg(MetaSheet("varsaw2", "varsaw", PostingTypes.PROSC))
sinepad = cmp.reg(MetaSheet("sinepad1", "sinepad", PostingTypes.PROSC))
rhodes = cmp.reg(MetaSheet("FMRhodes1", "FMRhodes1", PostingTypes.PROSC))
borch = cmp.reg(MetaSheet("BorchBattery", "BorchBattery", PostingTypes.MIDI))
drsix = cmp.reg(MetaSheet("drsix", "DR660", PostingTypes.SAMPLE, False))
nintendo = cmp.reg(MetaSheet("nintendo_soundfont1", "nintendo_soundfont", PostingTypes.MIDI, False))
nintendo2 = cmp.reg(MetaSheet("nintendo_soundfont2", "nintendo_soundfont", PostingTypes.MIDI, False))
xtndo = cmp.reg(MetaSheet("xtndo1", "xtndo", PostingTypes.SAMPLE, False))
modeAudio = cmp.reg(MetaSheet("modeAudio1", "ModeAudio", PostingTypes.SAMPLE, False))
# lfomul, hpf, lfow, pan
modulOSC = cmp.reg(MetaSheet("mosc1", "modulOSC", PostingTypes.PROSC))
# attT, susL, decT, relT, hpf, lpf 
stockSaw = cmp.reg(MetaSheet("ssaw1", "stockSaw", PostingTypes.PROSC))
stockSaw2 = cmp.reg(MetaSheet("ssaw2", "stockSaw", PostingTypes.PROSC))

# TODO: Currently dealing with buses 
# "gentle intro to supercollider" touches uppon it best
# Basically, only the first two buses produce sound, 0 being a sort of "master out"
# To properly apply things selectively, "routing" appears to be the answer 
# This would mean sending a synth to a buffer (e.g. 55) and then
# having an effect take 55 as input, apply its effect and then output to 0
# In fact they do this with reverb in the "The Bus Object" chapter
# Buses 0-15 are reserved for sound card slots, so you can grab any from 16-127
# Below example of blipp/reverb should demonstrate this effect, but not also that 
# re-applying the same effect will fuck the sound up since you get multiple reads 
# (there might be something here about order of execution for the subsequent reverbs)

chaoscillator.sheet("0s 1s 2s 1s 1s 8s 1", MAJOR, 4).all("#1.5 >2 pan05 bus40").tagged("s", "=.5")
organReed.sheet("4z 2z 0 4 5 4 . 8z 3z 1 4 3 4", MAJOR, 7).all("=4.0 >8.0").tagged("z", "=0")
#sinepad.sheet("0 1s 3 0s 1 . 0 2s 3 2s 1", MAJOR, 6).tagged("s", "=.5 >1").all("bus40")
#rhodes.sheet("4s 4s 5 3l . 4t 4s 5t 6 7l . 4s 4s 5 3l . 4t 6s 4t 7 2l", MAJOR, 7).all("#2 =2.0 >4.0 bus20").tagged("t", "=.5").tagged("s", "=1.0").tagged("l", "=4.0")
#yamaha.sheet("14 16s 16s").all("bus20").tagged("s", "=.5")
#drsix.sheet("58 2 2 59").all("bus40 #1.5")
#moog.sheet("8 5", MAJOR, 7).all("=16 >6 #.4 pan-0.5")

client = PublisherClient()
client.add_effect([{"target": "effect_reverb", "args": {"inBus":20, "outBus": 0, "room": 0.2, "mix":0.7}}])
client.add_effect([{"target": "effect_reverb", "args": {"inBus": 40, "outBus": 0, "room": 1.0, "mix":0.5}}])
client.set_bpm(176)


#client.update_synths()

cmp.smart_sync([])

cmp.post_all()

