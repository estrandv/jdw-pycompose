from random import randint

from scales import *
from sheet import *
from meta_sheet import *
from composer import *
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
borch = cmp.reg(MetaSheet("BorchBattery", "BorchBattery", PostingTypes.MIDI, False))
drsix = cmp.reg(MetaSheet("drsix", "DR660", PostingTypes.SAMPLE, False))
nintendo = cmp.reg(MetaSheet("nintendo_soundfont1", "nintendo_soundfont", PostingTypes.MIDI, False))
nintendo2 = cmp.reg(MetaSheet("nintendo_soundfont2", "nintendo_soundfont", PostingTypes.MIDI, False))
xtndo = cmp.reg(MetaSheet("xtndo1", "xtndo", PostingTypes.SAMPLE, False))
modeAudio = cmp.reg(MetaSheet("modeAudio1", "ModeAudio", PostingTypes.SAMPLE, False))
borchBattery = cmp.reg(MetaSheet("borch1", "borch_sample", PostingTypes.SAMPLE, False))
simpleKick = cmp.reg(MetaSheet("simpleKick1", "simpleKick", PostingTypes.PROSC))
# lfomul, hpf, lfow, pan
modulOSC = cmp.reg(MetaSheet("mosc1", "modulOSC", PostingTypes.PROSC))
# attT, susL, decT, relT, hpf, lpf 
stockSaw = cmp.reg(MetaSheet("ssaw1", "stockSaw", PostingTypes.PROSC))
stockSaw2 = cmp.reg(MetaSheet("ssaw2", "stockSaw", PostingTypes.PROSC))
stockSquare = cmp.reg(MetaSheet("ssquare1", "stockSquare", PostingTypes.PROSC))
stockSine = cmp.reg(MetaSheet("ssine1", "stockSine", PostingTypes.PROSC))

# Note on BUS: 16-127 are virtual buses; anything played there must be routed to bus 0 
# to actually make sound. This is done by using the outBus of effects. 
client = PublisherClient()
client.add_effect([{"target": "effect_reverb", "args": {"inBus":20, "outBus": 0, "room": 0.4, "mix":0.4}}])
client.add_effect([{"target": "effect_reverb", "args": {"inBus": 40, "outBus": 0, "room": 0.8, "mix":0.5}}])

client.add_effect([{"target": "effect_distortion", "args": {"inBus": 44, "outBus": 0, "dist": 0.25}}])
client.add_effect([{"target": "effect_reverb", "args": {"inBus": 50, "outBus": 0, "room": 0.4, "mix":0.2}}])

client.add_effect([{"target": "effect_combDelay", "args": {"inBus": 16, "outBus":20, "echo": 0.55, "beat_dur": 0.2, "echotime": 0.4}}])

client.set_bpm(150)

cmp.pre_tag("t:=.25").pre_tag("s:=.5").pre_tag("q:=0").pre_tag("l:=2 >2").pre_tag("xl:=4 >5")

#stockSine.sheet("2q 0 1 6[#.5] 1 . 4q 2 6[#.5] 0 1 . 6[#.5] 3 1 6[#.5] . 0 1 0 4", MINOR, 7) \
 #   .all("=8 >2 attT.4 relT1 decT.4 susL.5 phase0.02 bus20")
#stockSquare.sheet("0 0[width.8] 2 (2/4/8/4)", MINOR, 5).all("#.3 >1")
#stockSine.sheet("0 0 0 0 0 0 0 (2/4/2/6)", MINOR, 7).all("=.5 #.5 bus16 hpf1200")
#stockSine.sheet("0 1 1 0 . 2 2 0 3 . 1 2 1 2 . 4 3 1 2", MINOR, 8).all("phase0.02 hpf1200")
#warsaw.sheet("2 4", MINOR, 5).all("=16 >16 #1 width.4 slideTime.4 bus40")
#drsix.sheet("22 8 (22/26)[#0.2] (8/3/6/35[#.8]t 33t)").all("=0.5 bus20")
modeAudio.sheet("0 (22/24)").all("bus40 =.25")
moog.sheet("0 0[#0.8 >1.3 bus16] 0 (4/2)[#0.8 >2]", MINOR, 6)
stockSine.sheet("0 0 0 0 0 0 0 (2/8)", MINOR, 7).all("=.5")

#borchBattery.sheet("2 3 4 2").all("#3 =2")

#sinepad.sheet("2 4[>2 #1.5] 1 0[>3 #1.3] 6 0[>2 #1.3] 3[#1.3] 6 2 6[>2 #1.5] 1 0[>3 #1.3] 7 0[>2 #1.3] 3[#1.3] 4", MINOR, 6).tag("s:>1").all("bus40")
#yamaha.sheet("20[#2]s 5[#0.8]s 8[#0.8]t 8t 26[#2]s").all("bus20")
#warsaw.sheet("0 0 0 0 0 0 0 2 1 1 1 1 1 1 1 2 0 0 0 0 0 0 0 3 1 1 1 1 1 1 1 2", MINOR, 5).all("=.5 >2 bus20")


#modeAudio.sheet("29 46z 29 35 . 29 46z 29 33s 35s").tag("z:#.7")
#moog.sheet("8s 8s 9 8 7 . 8 9 8 11 . 8 9 8 7 . 8 9 8 6", MAJOR, 6).all("#.6 bus20")
#blipp.sheet("6xl 4xl 2xl 8xl", MAJOR, 7).all("#.3 bus40")


# TODO: Smart sync takes forever 
cmp.smart_sync([])
#client.update_synths()


cmp.post_all()

