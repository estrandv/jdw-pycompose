from rest_client import *
from scales import *
from score import Score
from composer import Composer, PostingTypes
from random import randint

loop=16.0
bpm(120)

scale = MINOR

# Example song
cmp = Composer()
padder = cmp.new("padder", "blipp", PostingTypes.PROSC)
bass = cmp.new("bass", "blipp", PostingTypes.PROSC)
bass_assist = cmp.new("bass_assist", "blipp", PostingTypes.PROSC)
warsaw = cmp.new("warsaw", "warsawBass", PostingTypes.PROSC)
warsaw2 = cmp.new("warsaw2", "warsawBass", PostingTypes.PROSC)
moog = cmp.new("moog", "moogBass", PostingTypes.PROSC)
moog2 = cmp.new("moog2", "moogBass", PostingTypes.PROSC)
organ = cmp.new("organ", "longsaw", PostingTypes.PROSC)
yamaha = cmp.new("drum", "YHDX200", PostingTypes.SAMPLE)
korger = cmp.new("drum2", "KORGER1Samples", PostingTypes.SAMPLE)
korger2 = cmp.new("drum3", "KORGER1Samples", PostingTypes.SAMPLE)
yamaha2 = cmp.new("drum4", "YHDX200", PostingTypes.SAMPLE)
lead = cmp.new("lead", "longsaw", PostingTypes.PROSC)
lead2 = cmp.new("lead2", "longsaw", PostingTypes.PROSC)
varsaw = cmp.new("varsaw1", "varsaw", PostingTypes.PROSC)
varsaw2 = cmp.new("varsaw2", "varsaw", PostingTypes.PROSC)
sinepad = cmp.new("sinepad1", "sinepad", PostingTypes.PROSC)
rhodes = cmp.new("FMRhodes1", "FMRhodes1", PostingTypes.PROSC)
borch = cmp.new("BorchBattery", "BorchBattery", PostingTypes.MIDI)

tweak("warsawBass", {'att': 0.0, 'dec': 2.0, 'preamp': 0.3, 'detune': 1.00})
tweak("moogBass", {'gain': 0.6, 'pan': -0.1, 'chorus': 0.0, 'gate': 0.3,
                   'cutoff': 240})
tweak("varsaw", {'att': 0.4, 'rate': 0.0, 'fmod': 4.0, 'reverb': 0.8})
tweak("sinepad", {'gain': 4.0, 'att': 0.02})
tweak("FMRhodes1", {'gain': 0.2, 'mix': 0.2, 'lfoDepth': 0.5, 'lfoSpeed': 0.8,
                    'att': 0.45, 'inputLevel': 0.4, 'modIndex': 0.2})

# cdefgahcdef
# abcdefghijk
# cdeg = abce
#padder.pad(32.0)

woo = "(f5---c5---e5---b5---)~:3"
ripples = "(.e... a2... c... e2... b... c2... b... a2..) 5"
piano = "([bc]e-- [.a]eca ---- ---- ----  [bc]a-- [.a]bcb ----)~:3 6"
rhythm = "(aece aede)~:5 4"
beat = " j.d2. i... e.d2. [ii]... "
low_beat = "j...i...j...i..."
crackle = ".... [a.][ba]b .... ...."
crackle_short = "[aa2]a3//a4-"
riff = "((a[b~:3a][b~:3a][b~:3a] ce-c a-)2.. e...(a[b~:3a][b~:3a][b~:3a] ce-c a-)2.. e2...)~:3 5"

padder.pad(4.0)
cmp.sync()
sinepad.play(woo).reach(cmp.len())
cmp.sync()
sinepad.play(woo).reach(cmp.len())
varsaw.play(crackle).reach(cmp.len())
cmp.sync()
padder.pad(32.0)
sinepad.play(woo).reach(cmp.len())
varsaw.play(crackle).reach(cmp.len())
yamaha.play(low_beat).reach(cmp.len())
cmp.sync()
padder.pad(32.0)
varsaw.play(crackle_short)
yamaha.play(beat).reach(cmp.len())
warsaw.play(rhythm).reach(cmp.len())
cmp.sync()
moog.play(piano)
yamaha.play(beat).reach(cmp.len())
warsaw.play(rhythm).reach(cmp.len())
cmp.sync()
padder.pad(32.0)
yamaha.play(beat).reach(cmp.len())
warsaw.play(rhythm).reach(cmp.len())
rhodes.play(ripples).reach(cmp.len())
cmp.sync()
padder.pad(32.0)
yamaha.play(beat).reach(cmp.len())
moog.play(piano).reach(cmp.len())
warsaw.play(rhythm).reach(cmp.len())
varsaw.play(crackle)
cmp.sync()
padder.pad(64.0)
warsaw2.play(riff).reach(cmp.len())
sinepad.play(woo).reach(cmp.len())
yamaha.play(low_beat).reach(cmp.len())
yamaha2.play("f7")
cmp.sync()
sinepad.play(woo).reach(cmp.len())
yamaha.play(low_beat).reach(cmp.len())
varsaw.play(crackle)
cmp.sync()
moog.play(piano)
yamaha.play(low_beat).reach(cmp.len())
warsaw.play(rhythm).reach(cmp.len())
cmp.sync()
padder.pad(32.0)
yamaha.play(beat).reach(cmp.len())
warsaw.play(rhythm).reach(cmp.len())
varsaw.play(crackle)
bass.play("a4-------~:5 ....  .... e3--- ----~:5 .... .... a4-------~:5")
yamaha2.play("j5...")
cmp.sync()
yamaha.play(beat).reach(cmp.len())
warsaw.play(rhythm).reach(cmp.len())
cmp.sync()
padder.pad(64.0)
moog.play(piano).reach(cmp.len())
warsaw2.play(riff).reach(cmp.len())
sinepad.play(woo).reach(cmp.len())
rhodes.play(ripples).reach(cmp.len())
yamaha2.play("g5... ....")
cmp.sync()
padder.pad(64.0)
sinepad.play(woo).reach(cmp.len())
varsaw.play(crackle_short)
yamaha.play(low_beat).reach(cmp.len())
warsaw.play(rhythm).reach(cmp.len())
cmp.sync()
yamaha2.play("[g5g5]")
moog.play(piano).reach(cmp.len())
sinepad.play(woo).reach(cmp.len())
yamaha.play(low_beat).reach(cmp.len())
cmp.sync()
bass.play("a4-------~:5")
yamaha2.play("f7")
padder.pad(32.0)

#yamaha.play(beat).reach(cmp.len())

#korger.play("a8")


###
rhodes.scale(scale)
sinepad.scale(scale)
varsaw.scale(scale)
varsaw2.scale(scale)
moog.scale(scale)
warsaw.scale(scale)
warsaw2.scale(scale)
lead2.scale(scale) # Was pretty fun in major thou tbh
lead.scale(scale)
bass_assist.scale(scale)
organ.scale(scale)
bass.scale(scale)
cmp.post_all()
reset()

# Example simple sequencer usage:
#Score().play("(d..[.d]d[.e]g2-)!:5 4").scale(scale).post_prosc("c", "blipp")

#test()
