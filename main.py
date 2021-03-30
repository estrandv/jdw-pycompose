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

blipp.section().in_octave(6).def_ovr({"reserved_time": 0.5, "rate": 2.0}).in_scale(MINOR) \
    .note(6, res=0.25).interpolate({"amp": 0.7}, 3).note(6).note(8, res=0.25).x(2) \
    .note(6, res=0.25).interpolate({"amp": 0.7}, 3).note(6).note(9, res=0.25).x(2) \
    .note(6, res=0.25).interpolate({"amp": 0.7}, 3).note(6).note(8, res=0.25).x(2) \
    .note(6, res=0.25).interpolate({"amp": 0.7}, 3).note(6).note(5, res=0.25).x(2)

blipp.repeat_last()

cmp.sync()

warsaw.section().def_ovr({"reserved_time": 2.0, "sus": 4.0, "amp": 0.25}).in_octave(5).in_scale(MINOR) \
    .note(8) \
    .note(6) \
    .note(5) \
    .note(9, res=0.5).pad(0.5).note(8, res=0.5, sus=2.0, amp=0.3).note(9, res=0.5) \

cmp.play(blipp, 2).play(warsaw).sync()

#yamaha.section().in_octave(0).note(6, res=8.0, amp=1.2)

#cmp.play(blipp, 2).play(warsaw, 2).play(yamaha).sync()

rhodes.section().in_octave(7).def_ovr({"amp": 2.0}).in_scale(MINOR) \
    .note(6).x(2).pad(0.5).note(8, res=0.5).note(4) \
    .note(6).x(2).pad(0.5).note(11, res=0.5).note(4) \

cmp.play(blipp, 2).play(warsaw, 2).play(rhodes).sync()


#korger.section().in_octave(0).note(4, res=0.5).interpolate({"amp": 1.4}, 14).note(14, res=0.5)

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
reset() ###### RESET CALLED HERE

# Example simple sequencer usage:
#Score().play("(d..[.d]d[.e]g2-)!:5 4").scale(scale).post_prosc("c", "blipp")

#test()
