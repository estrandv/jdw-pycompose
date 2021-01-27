from rest_client import *
from scales import *
from score import Score
from composer import Composer, PostingTypes

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
drum = cmp.new("drum", "YHDX200", PostingTypes.SAMPLE)
drum2 = cmp.new("drum2", "KORGER1", PostingTypes.SAMPLE)
drum3 = cmp.new("drum3", "KORGER1Samples", PostingTypes.SAMPLE)
drum4 = cmp.new("drum4", "YHDX200", PostingTypes.SAMPLE)
lead = cmp.new("lead", "longsaw", PostingTypes.PROSC)
lead2 = cmp.new("lead2", "longsaw", PostingTypes.PROSC)

tweak("warsawBass", {'att': 0.2, 'dec': 0.0})
warsaw.play("a5-..")

#warsaw.play("g5---")
#warsaw2.play("([ba][bb][bb][bb])~:3 6")
#moog.play("a4---------")
#bass.play(".a6-")
#bass.play("(bbbb)3")
#bass_assist.play("a4")
#drum.play("jjjj")
#drum4.play("e5...")
#moog.play("(a.g.[eg].b2.[.c][b2c]g-.ij.h-)5")
#drum.play("[c3j!!!hj!!!]").reach(cmp.len())
#drum2.play("c...")

###


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
