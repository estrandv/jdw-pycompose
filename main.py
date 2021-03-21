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


#tweak("warsawBass", {'att': 0.5, 'dec': 1.0, 'preamp': 0.2, 'detune': 1.01})
#tweak("moogBass", {'gain': 0.0, 'pan': -0.1, 'chorus': 0.0, 'gate': 0.1, 'cutoff': 280})
#tweak("varsaw", {'att': 0.4, 'rate': 0.0, 'fmod': 4.0, 'reverb': 0.8, 'gain': 0.4})
#tweak("sinepad", {'gain': 8.0, 'att': 0.05})
#tweak("longsaw", {'gain': 0.2, 'att': 0.05})
#tweak("FMRhodes1", {'gain': 0.2, 'mix': 0.2, 'lfoDepth': 0.5, 'lfoSpeed': 2.0, 'att': 0.02, 'inputLevel': 0.4, 'modIndex': 0.2})

#tweak("YHDX200", {'att': 0.0, 'rel': 0.02, 'start': 0.2, 'loop': 0, 'rate': 1.0})
#tweak("KORGER1Samples", {'att': 0.02, 'rel': 0.02, 'start': 0.2, 'loop': 0, 'rate': 2.0})
#tweak("DR660", {'att': 0.02, 'rel': 0.02, 'rate': 0.8})


# cdefgahcdef
# abcdefghijk
# cdeg = abce
# Testing some new format stuff here
import pscore

# TODO: 
    # interpolate() call which moves given attributes between note() and note() by given steps 
    # No attributes mandatory (except maybe reserved_time) 
    # Renames and refactoring

s2 = pscore.Score().section() \
        .def_ovr({"att": 0.03, "sus": 1.3, "amp": 1.2, "reverb": 0.2}) \
        .in_octave(6) \
    .note(6, res=0.5).note(8, res=0.5).x(2).note(2, res=0.5).note(8).note(7) \
    .note(4, res=0.5).note(7, res=0.5).x(2).note(6, res=0.5).note(9).note(7).parent \
    #.note(0, res=0.1).interpolate({"tone": 182.0}, 39) \
    #.note(0, res=0.5).note(3, res=0.5).x(2).note(6, res=0.5).note(4).note(5).parent


drums = pscore.Score().section() \
        .def_ovr({"reserved_time": 0.5, "amp": 2.0}).in_octave(0) \
        .note(4).x(3).note(28).until_total(s2.len()).parent

post_prosc("jupp", "jupp", s2.export("varsaw"))
#post_prosc("blipp", "blipp", score.export("moogBass"))
post_sample("dr", "dr", drums.export("KORGER1Samples"))


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
#cmp.post_all()
#reset() ###### RESET CALLED HERE

# Example simple sequencer usage:
#Score().play("(d..[.d]d[.e]g2-)!:5 4").scale(scale).post_prosc("c", "blipp")

#test()
