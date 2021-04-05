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


# TODO:
# x. Add stop and reset keybinds to i3 
# 2. Add better decimal conversion to parsed numbers starting with 0 

bpm(140)

from sheet import Sheet

sht = Sheet("0 2 4 2 . 0 2 6 2 . 0 2 10 2 . 0 2 11 2 . 0 2 4 2 . 0 2 6 2 . 0 2 10 2 . 0 2 9 2")
sht.part_step([3,4], "=10 >25")
sht.part_step([1], ">025 #15")
sht.part_step([4], "chorus08")
longsaw.section().in_scale(MINOR).in_octave(5).def_ovr({"reserved_time": 0.5}).absorb(sht)


s2 = Sheet("2 0 2 4 9 11")
s2.part_step([4,5,6], "=20 >45 #06 fmod10")
s2.part_step([6], "reverb07 #08")
varsaw.section().def_ovr({"reserved_time": 6.0, "sus": 9.0, "amp": 0.7}).in_scale(MINOR).in_octave(6) \
        .absorb(s2)

#korger.section().txt("58").pad(1.0).txt("111")

s3 = Sheet("0 1 1 0 1 1 2 1 1 2 1 1 2 3")
s3.part_step([13,14], "=60 >60 #06")
warsaw.section().in_scale(MINOR).in_octave(8).absorb(s3)

s4 = Sheet("4")
s4.part_step([1], ">240 =240 #02 att20 chorus10")
moog.section().in_octave(8).in_scale(MINOR).absorb(s4)

yamaha.section().in_octave(0).txt("14 #08").x(2).txt("95").until(longsaw.len())

#blipp.section().in_octave(5).in_scale(MAJOR).note(5, sus=0.5).x(3).note(11, sus=0.5)

cmp.mute(
    warsaw,
    moog,
    yamaha,
    varsaw,
    longsaw
)

cmp.sync()




# cdefgahcdef
# abcdefghijk
# cdeg = abce
# Testing some new format stuff here

# TODO: 
    # No attributes mandatory (except maybe reserved_time) 
    # Renames and refactoring

#cmp.stop()

#reset()
cmp.post_all()
#reset()

#reset() ###### RESET CALLED HERE

# Example simple sequencer usage:
#Score().play("(d..[.d]d[.e]g2-)!:5 4").scale(scale).post_prosc("c", "blipp")

#test()
