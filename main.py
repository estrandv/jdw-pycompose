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
lead = cmp.new("lead", "longsaw", PostingTypes.PROSC)

### 
padder.pad(16.0)
bass.play("( d..[.d] d[.e]g2- )!:5 4").reach(cmp.len())
cmp.sync()
padder.pad(24.0)
bass.play_latest().reach(cmp.len())
bass_assist.play("([.a]fa2g [.c]fc2g)!:5 5").reach(cmp.len())
cmp.sync()
drum.play(" .... ...[..i!!h] ")
bass.play_latest().reach(cmp.len())
bass_assist.play_latest().reach(cmp.len())
cmp.sync()
padder.pad(16.0)
bass.play_latest().reach(cmp.len())
drum.play("(jkak [jj]kak)").reach(cmp.len())
drum2.play("c")
cmp.sync()
padder.pad(16.0)
bass.play_latest().reach(cmp.len())
drum.play_latest().reach(cmp.len())
organ.play("(aeeegeee)~:3 5").reach(cmp.len())
drum2.play("c")
cmp.sync()
padder.pad(16.0)
lead.play("([aaaa][eaac]ge [aaaa][eaac]de)~:2 7").reach(cmp.len())
bass.play_latest().reach(cmp.len())
drum.play_latest().reach(cmp.len())
drum2.play("c")
cmp.sync()
padder.pad(16.0)
lead.play_latest().reach(cmp.len())
organ.play_latest().reach(cmp.len())
bass.play_latest().reach(cmp.len())
drum.play_latest().reach(cmp.len())
drum2.play("c!!![dd][dd][dd]")
cmp.sync()
drum2.play("c... ....")
drum.play("h.h. [hhh.]...")
organ.play("d9d9d9")
cmp.sync()

###

lead.scale(scale)
bass_assist.scale(scale)
organ.scale(scale)
bass.scale(scale)
cmp.post_all()
reset()


# Example simple sequencer usage:
#Score().play("(d..[.d]d[.e]g2-)!:5 4").scale(scale).post_prosc("c", "blipp")

#test()