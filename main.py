from rest_client import *
from scales import *
from score import Score
from composer import Composer, PostingType, PostingTypes
from random import randint
import pscore

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

yamaha.section().in_octave(0).in_scale(CHROMATIC).txt("18 =05 #02").txt("38 =20 #05").cut(2).txt("6 =15 #07 >20").cut(2) \
        .txt("18 =10 #02").cut(2).txt("39 =05 #08").cut(2).pad(2.0).txt("35 =05 #10").until(16.0)

moog.section().in_scale(MINOR).txt("20 =30 >40 pan08").txt("21 =05 >10").cut(2).txt("19 =10 >20").txt("24 =35 >10") \
        .txt("16 =15").txt("8 =10").cut(2).txt("22 =05 >05").txt("24 =50 >55 #07").cut(2)

rhodes.section().in_scale(MINOR).txt("23 =15 >55 lfoDepth22 #28").cut(2).txt("33 =65 >70 #28")

sinepad.section().in_octave(6).in_scale(MINOR).pad(4.0).txt("4 =20 >40 #05 att02").txt("5 =20 >40 #03")

warsaw.section().in_octave(5).in_scale(MINOR).txt("0 =05 att10").interpolate({"tone": 44.0, "att": 0.5}, 8)

korger.section().in_octave(0).txt("14 #14")


cmp.sync()

#yamaha.section().in_octave(0).note(8, sus=0.5).x(3).note(7, sus=0.5)



# cdefgahcdef
# abcdefghijk
# cdeg = abce
# Testing some new format stuff here

# TODO: 
    # No attributes mandatory (except maybe reserved_time) 
    # Renames and refactoring


cmp.post_all()
#reset() ###### RESET CALLED HERE

# Example simple sequencer usage:
#Score().play("(d..[.d]d[.e]g2-)!:5 4").scale(scale).post_prosc("c", "blipp")

#test()
