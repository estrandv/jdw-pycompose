from rest_client import *
from scales import *
from score import Score
from composer import Composer, PostingTypes
from random import randint

loop=16.0
bpm(140)

scale = MAJOR

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
drum = cmp.new("drum", "YHDX200", PostingTypes.SAMPLE)
drum2 = cmp.new("drum2", "KORGER1", PostingTypes.SAMPLE)
drum3 = cmp.new("drum3", "KORGER1Samples", PostingTypes.SAMPLE)
drum4 = cmp.new("drum4", "YHDX200", PostingTypes.SAMPLE)
lead = cmp.new("lead", "longsaw", PostingTypes.PROSC)
lead2 = cmp.new("lead2", "longsaw", PostingTypes.PROSC)
varsaw = cmp.new("varsaw1", "varsaw", PostingTypes.PROSC)
varsaw2 = cmp.new("varsaw2", "varsaw", PostingTypes.PROSC)
sinepad = cmp.new("sinepad1", "sinepad", PostingTypes.PROSC)
rhodes = cmp.new("FMRhodes1", "FMRhodes1", PostingTypes.PROSC)
borch = cmp.new("BorchBattery", "BorchBattery", PostingTypes.MIDI)

#tweak("warsawBass", {'att': 0.2, 'dec': 2.0, 'preamp': 4.0, 'detune': 1.00})
tweak("moogBass", {'gain': 1.8, 'pan': 0, 'chorus': 0.1, 'gate': 0.5, 'cutoff': 1200})
#tweak("varsaw", {'att': 0.0, 'rate': 0.09, 'fmod': 0.0, 'reverb': 0.1})
tweak("sinepad", {'gain': 3.0, 'att': 0.02})
tweak("FMRhodes1", {'gain': 2.0, 'mix': 0.2, 'lfoDepth': 0.2, 'lfoSpeed': 0.8, 'att': 0.5, 'inputLevel': 0.4, 'modIndex': 0.2})

# cdefgahcdef
# abcdefghijk
# cdeg = abce
#rhodes.play("(a-[ac][a.] be[bc]b -e2ab [.a]b[ec]e)7")
#warsaw.play("(g.g.e2.e2.g.g.e.e.)5")
#bass.play("(i-------e-------)6")
#moog.play("([.e][eg].. [.e][hg].. [.e][fc].. [.e][hj][g.].)7")
#varsaw.play("([ee][ee][ee][ec][aa][aa][aa][ac])~:3 4").reach(cmp.len())
#sinepad.play("( e2-b2- c2-ab2 )5").reach(cmp.len())
#drum.play("[d5!!.d5d5!]d5..").reach(cmp.len())
#drum2.play("dg").reach(cmp.len())
#cmp.start_here()
#rhodes.play("(aaabcccbeeebccc)5")
#drum4.play("([bc][ab])5").reach(cmp.len())
#cmp.start_here()
#sinepad.play("(cda.c[da]b.)6")

#bass.play("(e---b---e[.f][g.]hg-f i)~:3 6")
rhodes.play("((ebab)xx7 (abcb)7 )!!!")
moog.play("(e4--- ---- ---- a5---)~:3")
moog2.play("(h4--- ---- ---- e4---)~:3")
#drum2.play("d.").reach(cmp.len())
#drum.play("j.").reach(cmp.len())
borch.play("k.")

#drum4.play("([a!f!!][a!f][a!af!.][a!f])7")
#drum.play("([a!f!!][a!f][a!af!.][a!f])2")

#sinepad.play("a6...")

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
