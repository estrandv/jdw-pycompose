from rest_client import *
from scales import *
from score import Score
from composer import Composer, PostingTypes

loop=16.0
bpm(120)

scale = MINOR

# Example song
cmp = Composer()
bass = cmp.new("bass", "blipp", PostingTypes.PROSC)
organ = cmp.new("organ", "longsaw", PostingTypes.PROSC)
#t: Score = cmp.new("tomato", "longsaw", PostingTypes.PROSC)
#s.play("(c.cc) 5").reach(8.0)
#cmp.sync()
#s.play("(d.dd)5")
#cmp.sync()
#t.play("(a-a-d-d-)~:3 6")
#s.play("([cc])5").reach(cmp.len())
#cmp.post_all()
#reset()



# Example simple sequencer usage:
#Score().play("(d..[.d]d[.e]g2-)!:5 4").scale(scale).post_prosc("c", "blipp")

#ScoreBuilder().("(d..[.d]d[.e]g2-)!:5 4").scale(scale).post_prosc("c", "blipp")
#Score("M([.a]fa2g [.c]fc2g)!:5 5").scale(scale).post_prosc("coplo", "blipp")
#Score("M(aeeegeee)~:3 5").scale(scale).post_prosc("cizz", "longsaw")
#Score("M(.a.e .a.g)~:3 6").scale(scale).post_prosc("cizza", "longsaw")
#Score("M([aaaa][eaac]ge [aaaa][eaac]de)~:2 7").scale(scale).post_prosc("diiz", "longsaw")
#Score("M(e[cd]ddee[ed]d)").post_sample("do", "KORGER1")
#Score("M(d.d[.j]d.d[.j])").post_sample("doc", "KORGER1Samples")
#Score("M(jkak [jj]kak)").reach(8.0).post_sample("dop", "YHDX200")

#reset()


#test()