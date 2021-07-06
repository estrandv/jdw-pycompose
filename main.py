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
client.add_effect([{"target": "effect_reverb", "args": {"inBus": 40, "outBus": 0, "room": 0.9, "mix":0.8}}])

client.add_effect([{"target": "effect_distortion", "args": {"inBus": 44, "outBus": 0, "dist": 0.08}}])
client.add_effect([{"target": "effect_reverb", "args": {"inBus": 50, "outBus": 0, "room": 0.4, "mix":0.2}}])

client.add_effect([{"target": "effect_combDelay", "args": {"inBus": 16, "outBus":40, "echo": 0.55, "beat_dur": 0.2, "echotime": 0.4}}])

client.set_bpm(180)

cmp.pre_tag("t:=.25").pre_tag("s:=.5").pre_tag("q:=0").pre_tag("l:=2 >2").pre_tag("xl:=4 >5").pre_tag("_:#0")

# TODO: Sample listing is still tricky 
#   - Include name on every line for grepping
#   - Sort samples by kick,cymbal etc 

#stockSaw.sheet("0s 0s 0 0 (4t 4t 3t 4t/5/6)", MAJOR, 6).all(">1.2 lfoS1.2 lfoD2")

#stockSaw.sheet("0s 0t 0t (1s/3s/6s/2s) 0t 0t", MINOR, 5).all("#1.2 lfoS6 lfoD0.4 pan-0.3 >0.2")
#stockSine.sheet("1 (2/4) 0q 3 7q 4 4 8q 3 2 (1/1q 6)", MAJOR, 6).all("=4 #0.8 attT0.1 relT4 lfoD0.4 lfoS2 susL0.8 decT0.1 hpf800 pan0.2")
#moog.sheet("0 (0/0_) 0[pan0.5] (0/3/0/5) (0[bus40]/0) 0[bus40] 0[pan-0.5] (2/6/4/8)[bus20]", MAJOR, 6).all("#0.7").tag("_:#0")
#moog.sheet("0t 0t 4s (7xxl/9xxl/6xxl/2xxl)", MAJOR, 6).all("#0.5 bus44").tag("xxl:=7 >5 pan0.5")
#moog.sheet("2[=7 >6] 3[=0.5 >2] 4[=3.5 >4] 7[=0.5] (9/5/6/12)[=4.5 >5]", MAJOR, 6).all("#0.4 chorus0.1")

#moog.sheet("0g 6q 2 0g 8q 4 0g 11q (6/2/4/2) 0g 8q 4", MAJOR, 6).all("=2 >1.5").tag("q:>6 #0.5 chorus0.2 cutoff200").tag("g:pan-0.2 #0.8 >4")

#stockSaw.sheet("0 0 0 0 0 0 0 (8/9/12/14)", MAJOR, 6).all("=0.5 lpf2800 hpf400 lfoD4.8 lfoS1.5 >0.125 attT0.1 relT0.2 decT0.0 susL0.5")#.tag("g:=0.125 relT2 bus16")
#yamaha.sheet("9[pan0.3] 10[#1.4 pan0.2]t 10t 10s 10[pan-0.3] (11/22s 23s/11/51s 22t 16t)").all("bus20 #6 pan0.8 rate1.4 pan0.5").tag("t:pan-0.3").tag("s:pan0.3")

padder.pad(64.0)
#drsix.sheet("72q 10[#0.7]s 10[bus20]s 10[#1.2]s 10s 67q 10[#0.8]s 10s 10[#0.4]s 10s").all("start200")
drsix.sheet("10[#1.8 pan0.3]s 10[#2.2 pan0.2]s (66[#0.8]/66[#1.2]s 66s) (23/24)[pan-0.2] 66").all("start0.2 rate1.1")
#korger.sheet("7[#4]q 66[#0.8]h 66h 10[#2]q 66[#0.8]h 66h (23q/21q) 66[#0.9]h 66h 19q 66[#0.8]h 66h").all("att0.3 rate1.1").tag("h:=0.5")

#warsaw.sheet("0t 0t 0t 0t 0t 0t 0t 8t", MINOR, 8).all("#0.5 =0.5 pan0.8 bus16")
cmp.smart_sync([])
#client.update_synths()



client.nrt_record(drsix.to_nrt(), 180, "test_emil.wav", "sample")

#cmp.post_all()

