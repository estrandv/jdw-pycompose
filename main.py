from rest_client import *
from scales import *
from score import Score
from composer import Composer, PostingType, PostingTypes
from random import randint

loop=16.0
bpm(130)

scale = MINOR

# Example song
cmp = Composer()
padder = cmp.new("padder", "blipp", PostingTypes.PROSC)
blipp = cmp.new("bass", "blipp", PostingTypes.PROSC)
blipp2 = cmp.new("bass_assist", "blipp", PostingTypes.PROSC)
warsaw = cmp.new("warsaw", "warsawBass", PostingTypes.PROSC)
warsaw2 = cmp.new("warsaw2", "warsawBass", PostingTypes.PROSC)
moog = cmp.new("moog", "moogBass", PostingTypes.PROSC)
moog2 = cmp.new("moog2", "moogBass", PostingTypes.PROSC)
organ = cmp.new("organ", "longsaw", PostingTypes.PROSC)
yamaha = cmp.new("drum", "YHDX200", PostingTypes.SAMPLE)
yamaha2 = cmp.new("drum4", "YHDX200", PostingTypes.SAMPLE)
korger = cmp.new("drum2", "KORGER1Samples", PostingTypes.SAMPLE)
korger2 = cmp.new("drum3", "KORGER1Samples", PostingTypes.SAMPLE)
simple_korg = cmp.new("simple_korg", "KORGER1", PostingTypes.SAMPLE)
longsaw = cmp.new("lead", "longsaw", PostingTypes.PROSC)
longsaw2 = cmp.new("lead2", "longsaw", PostingTypes.PROSC)
varsaw = cmp.new("varsaw1", "varsaw", PostingTypes.PROSC)
varsaw2 = cmp.new("varsaw2", "varsaw", PostingTypes.PROSC)
sinepad = cmp.new("sinepad1", "sinepad", PostingTypes.PROSC)
rhodes = cmp.new("FMRhodes1", "FMRhodes1", PostingTypes.PROSC)
borch = cmp.new("BorchBattery", "BorchBattery", PostingTypes.MIDI)
drsix = cmp.new("drsix", "DR660", PostingTypes.SAMPLE)

reset() ###### RESET CALLED HERE

tweak("warsawBass", {'att': 0.5, 'dec': 1.0, 'preamp': 0.2, 'detune': 1.01})
tweak("moogBass", {'gain': 0.0, 'pan': -0.1, 'chorus': 0.0, 'gate': 0.1, 'cutoff': 280})
tweak("varsaw", {'att': 0.4, 'rate': 0.0, 'fmod': 4.0, 'reverb': 0.8, 'gain': 0.4})
tweak("sinepad", {'gain': 8.0, 'att': 0.05})
tweak("longsaw", {'gain': 0.2, 'att': 0.05})
tweak("FMRhodes1", {'gain': 0.2, 'mix': 0.2, 'lfoDepth': 0.5, 'lfoSpeed': 2.0, 'att': 0.02, 'inputLevel': 0.4, 'modIndex': 0.2})

tweak("YHDX200", {'att': 0.0, 'rel': 0.02, 'start': 0.2, 'loop': 0, 'rate': 1.0})
tweak("KORGER1Samples", {'att': 0.02, 'rel': 0.02, 'start': 0.2, 'loop': 0, 'rate': 2.0})
tweak("DR660", {'att': 0.02, 'rel': 0.02, 'rate': 0.8})


# cdefgahcdef
# abcdefghijk
# cdeg = abce
padder.pad(32.0)
varsaw.play("(b//c------.// .... .... b//a------.//  .... ....) 6")
warsaw.play("(.c.c d.a. .c.c d.ge .c.c d.a. .c.c b.ab)~:3 6").reach(cmp.len())
sinepad.play("([a~e].[a~e][c~e] a~bdb [a~e].[a~e][c~e] g~bab )~ 5").reach(cmp.len())
rhodes.play("(.... ...[ag]~:5 .... .... .... ...[ac]~:5 .... ....) 7")
moog.play("(..g- ..b. ..d. ..b. ..g- ..e. ..b. ..c.) 5").reach(cmp.len())
warsaw2.play("(.... [aa].a. ..[aa]. b... .... [aa].a. ..[aa]. ....) 5").reach(cmp.len())
blipp.play("g2--- .... g2--- d2---").reach(cmp.len())

cmp.start_here()
#drsix.play("([c.cc])3")
cmp.sync()
drsix.play("(a3c3)xxxxxx [a3c3][c3.c3c3]").reach(cmp.len())
cmp.sync()
drsix.play("(a3c3)xxxxxx [a3c3][c3.c3c3]").reach(cmp.len())
moog.play("([e~b!]xxx [a~b!]xxx) 3").reach(cmp.len())
cmp.sync()
drsix.play("(a3c3)xxxxxx [a3c3][c3.c3c3]").reach(cmp.len())
moog.play_latest().reach(cmp.len())
warsaw.play("(g--- a--- c--- b---) 7")
warsaw2.play("(i-i- c-c- e-e- d-d-) 7")
cmp.sync()
drsix.play("(a3c3)xxxxxx [a3c3][c3.c3c3]").reach(cmp.len())
longsaw.play("(e--[eb] g--[jd] eee[eb] [be]g--)~:3 7")
moog.play_latest().reach(cmp.len())
korger.play("e5")
warsaw.play("(g--- a--- c--- b---) 7")
warsaw2.play("(i-i- c-c- e-e- d-d-) 7")
blipp.play("a5-------")
cmp.sync()
cmp.play(drsix, warsaw, warsaw2, moog)
sinepad.play("([ae][.a]a. [ge][.a]a [be][.a]a. [ce][.a]a. ) 5")
varsaw.play("(g[abcd].. e[abce].. g.ga3 c[abce]..) 6")
cmp.sync()

#warsaw.play("(.[bc].. .[bc]a. .b.. .[bc][be]. .g.g .[bc].. .[bc]e. [bc]a..) 6")
#rhodes.play("(b... e... a... b... e... c... b... a...) 5")
#sinepad.play("(..[ge]a ..bb ..[gb]a .a..)5").reach(cmp.len())
#yamaha.play("g...").reach(cmp.len())
#korger.play("c.e.c.[j2e].").reach(cmp.len())
#moog.play("a4b4..")

rhodes.scale(scale)
sinepad.scale(scale)
varsaw.scale(scale)
varsaw2.scale(scale)
moog.scale(scale)
warsaw.scale(scale)
warsaw2.scale(scale)
longsaw.scale(scale) # Was pretty fun in major thou tbh
longsaw2.scale(scale)
blipp2.scale(scale)
organ.scale(scale)
blipp.scale(scale)
cmp.post_all()

# Example simple sequencer usage:
#Score().play("(d..[.d]d[.e]g2-)!:5 4").scale(scale).post_prosc("c", "blipp")

#test()
