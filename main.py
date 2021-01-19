from rest_client import *
from scales import *
from score import Score
from composer import Composer, PostingTypes

loop=16.0
bpm(140)

scale = MINOR

# Example song
cmp = Composer()
padder = cmp.new("padder", "blipp", PostingTypes.PROSC)
bass = cmp.new("bass", "blipp", PostingTypes.PROSC)
bass_assist = cmp.new("bass_assist", "blipp", PostingTypes.PROSC)
organ = cmp.new("organ", "longsaw", PostingTypes.PROSC)
drum = cmp.new("drum", "YHDX200", PostingTypes.SAMPLE)
drum2 = cmp.new("drum2", "KORGER1", PostingTypes.SAMPLE)
drum3 = cmp.new("drum3", "KORGER1", PostingTypes.SAMPLE)
lead = cmp.new("lead", "longsaw", PostingTypes.PROSC)
lead2 = cmp.new("lead2", "longsaw", PostingTypes.PROSC)

padder.pad(4.0)
cmp.sync()
### 
padder.pad(24.0)
bass.play("( d..[.d] d[.e]g2- )!:5 4").reach(cmp.len())
cmp.sync() # Enter bass assist 
padder.pad(16.0)
bass.play_latest().reach(cmp.len())
bass_assist.play("([.a]fa2g [.c]fc2g)!:5 5").reach(cmp.len())
drum2.play("[dd]d")
cmp.sync() # Same, but end with drumstart
bass.play_latest().reach(cmp.len())
bass_assist.play_latest().reach(cmp.len())
drum.play(" .... ...[..i!!h] ")
cmp.sync() # Break: Enter organ with a cymbal
padder.pad(16.0)
drum.play_latest().reach(cmp.len())
organ.play("(aeeegeee)~:3 5").reach(cmp.len())
drum2.play("c")
cmp.sync() # Enter solo riff buildup
lead.play("([a!aaa][e!aac]ge)~:2 7")
drum2.play("c")
cmp.sync() # Keep building with hihat tap
padder.pad(16.0)
lead2.play("([a!aaa][e!aac])~:2 6").reach(cmp.len())
drum.play_latest().reach(cmp.len())
drum2.play("c!!!")
drum3.play("[dd!!d.]").reach(cmp.len())
cmp.sync() # Bombastic chorus
drum2.play("[cg]... .... dc")
padder.pad(32.0)
lead.play("([a!aaa][e!aac]ge [a!aaa][e!aac]de)~:2 7").reach(cmp.len())
drum.play("jkak [jj]kak").reach(cmp.len())
organ.play("a8--- ---- g7--- d7--- a7--- ----")
cmp.sync() # Slow down, but keep the nasty drums
padder.pad(32.0)
organ.play("([aa][aa]ac e[ee]ed)~:3 5").reach(cmp.len())
drum.play("(.k.k [jj]k.k)").reach(cmp.len())
drum2.play("gj") # xD
cmp.sync() # Bring back the bass blip
padder.pad(32.0)
bass.play_latest().reach(cmp.len())
bass_assist.play_latest().reach(cmp.len())
organ.play_latest().reach(cmp.len())
drum.play_latest().reach(cmp.len())
cmp.sync() # Rev that lead a bit
padder.pad(32.0)
lead2.play("([a!aaa][e!aac].. .... [a!aaa][e!aac].. ....)~:2 7").reach(cmp.len())
bass.play_latest().reach(cmp.len())
bass_assist.play_latest().reach(cmp.len())
organ.play_latest().reach(cmp.len())
drum.play("jkak [jj]kak").reach(cmp.len())
drum2.play("gg!!!!")
cmp.sync()
drum2.play("c... ....")
drum.play("h.h. [hhh.]...")
organ.play("d7d7d7")
cmp.sync() # Bombastic chorus
bass.play("g4--------")
drum2.play("[cggg]")
padder.pad(32.0)
lead.play_latest().reach(cmp.len())
drum.play("jkak [jj]kak").reach(cmp.len())
organ.play("a8--- ---- g7--- d7--- a7--- ----")
bass_assist.play("(g//[a!!dc!!!!d]c//)~:3 4").reach(cmp.len())
cmp.sync()
drum2.play("cbg. ....")
drum.play("h.h")
organ.play("[d7a7d6a6][d5a5]d4------- .... .[...j9]..")
cmp.sync()

###

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