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


#warsaw.sheet("5 6 2 4", MINOR, 8).all("#.3 >6.0 =8.0 bus20")
#moog.sheet("6 2t 7 2t 6 2t 5 2t", MINOR, 5).all(">8.0 =4.0 att.3 #.6 att.2").tagged("t", "=0 >5.0 att.4")
#blipp.sheet("4g 3 2g 0 4g 0 6g 0 1g 2 3g 0 5g 0 5g 0", MINOR, 7).all("#.5 >3.0 bus20").tagged("g", ">2.0 att.2")
stockSaw.sheet("0 2 0 2 0 4 0 4 0 3 0 3 0 4 0 4", MINOR, 5).all("bus40 #.8 =.5 attT.3 decT.3 susL2.0 lpf530 hpf300")
modeAudio.sheet("4s 4s 0 8 0").all("#1.5 bus40").tagged("s", "=.5")
#yamaha.sheet("26").all("#4.0 bus40")

client = PublisherClient()
client.add_effect([{"target": "effect_reverb", "args": {"inBus":20, "outBus": 0, "room": 0.2, "mix":0.7}}])
client.add_effect([{"target": "effect_reverb", "args": {"inBus": 40, "outBus": 0, "room": 1.0, "mix":0.4}}])


#client.update_synths()

cmp.smart_sync([yamaha])

cmp.post_all()
