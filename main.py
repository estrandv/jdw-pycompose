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

# It's still kinda clumsy 
# It would be nice if you could sketch notes 
# The core issue with "4==__" or suchlike is that you cannot go "below"
# You could always designate symbols, but you can't really get to a point of "length in letters equals length in beat"
# Anyway, youd have things like
# res up: = | res down: : | amp up: ! | amp down: . | sus up: _ | sus down: <

# Colon is actually rather nice for illustrating cut res since you get that amount of symbols (::: = 1/6)
# note("4:::>>>>") # Problem with sus of course is that relative becomes a bit hard to track. Then again it does not affect beat. 
# But yeah, if you want to make say "1/6 res with really long sus" there's no comfortable way to do that with a sketch 
# HOWEVER that's a bit of a special scenario anyway that note() might just work fine with 
# note("5===<<") # So this would be res=4.0, sus=2.0 but naturally there's an issue with fine-tuning sus as well 
# There could always be different resolutions for both sus and res. A 0.5 step as "-" or "[" 
# note("11===-<<[") would be... yeah, not as readable as I'd hoped.
# Thing about music theory is you have a symbol for every resolution level 
# note("11 =05 <06 !22") is far from readable in the same sense but has a certain charm when writing 
# note("11 =12 >11 #08") would be TONE:11, RES:1.2, SUS1.1 AMP: 0.8
# One of the worst parts of the new writing is counting the fucking notes though, "how much res so far?" and then you have 
# to infer it all the way though. It gets easier of course if it is spelled out everywhere and has a clear symbol, but "a4---..b4-" reads "8" like a boss 
# I think freeform text is a hella step up though. You can even run custom fields like it's nothing 
# note("6 ^4 =10 >12 @12 reverb18 gain14", default=True).note("6 =10 >12 ...")


# ::::
# ==== 

moog.section().in_octave(6).in_scale(MINOR).def_ovr({"sus": 8.0, "att": 0.25}) \
    .note(4, res=7.0).note(5).note(6, res=8.0) \
    .note(4, res=2.0).note(5, res=2.0).note(7, res=4.0).note(6, res=8.0) \

rhodes.section().in_octave(7).in_scale(MINOR).def_ovr({"sus": 16.0, "amp": 4.0}) \
    .note(2, res=6.5).note(0, res=3.5).note(1, res=2.0)

varsaw.section().in_octave(6).in_scale(MINOR).def_ovr({"sus": 2.0}) \
    .note(3).x(3).note(4, res=0.5).note(6, res=1.5).note(4).x(3) \
    .note(6, res=0.5).note(4, res=0.5).x(2).note(3, res=1.5) \
    .note(6, res=0.5).note(4, res=0.5).x(2).note(3, res=1.5) \
    .note(7).note(4) \

varsaw2.section().in_octave(4).in_scale(MINOR) \
    .pad(16.0) \
    .note(0, res=0.25, amp=0.4, sus=2.0).interpolate({"att":0.5, "amp": 1.2}, 31)

blipp.section().note(4, amp=2.4).x(32)
blipp2.section().note(8, amp=1.6, res=0.5).x(64)

sinepad.section().in_octave(7).in_scale(MINOR).def_ovr({"sus": 4.0, "amp": 0.4}) \
    .note(0).interpolate({"tone": 240.0}, steps=8)

moog2.section().in_octave(7).in_scale(MINOR).def_ovr({"chorus": 0.4, "cutoff": 480.0, "sus": 16.0, "res": 4.0, "amp": 0.5}) \
    .note(7).note(5).x(2).note(3)

korger.section().note(0)
korger2.section().note(1).interpolate({"amp": 0.8},6).note(2, res=0.5).x(2).note(1).x(23)

yamaha.section().in_octave(0).note(8, sus=0.5)


#korger.section().in_octave(0).note(4, res=0.5).interpolate({"amp": 1.4}, 14).note(14, res=0.5)

# MOOGS -> 

cmp.mute(
    korger, # Starting cymbal
    korger2, # HiHat
    yamaha, # Regular djungledrum
    sinepad, # Sinking water
    varsaw, # China Riff
    varsaw2, # Static warble
    #moog, # Dum, du-dum
    moog2, # Forest fairies
    blipp, # Djungle drum
    blipp2, # Rapid rhythmic beep-drum
    rhodes # Hesitant harpiscord, weak
)

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
