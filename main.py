from rest_client import *
from scales import *
from score import Score

loop=8.0
bpm(120)

# TODO: STILL wrong, even with test correct. Might be test expects the wrong thing.

Score("(abcd efgh i)~:3 4").reach(loop).scale(MAJOR).post_prosc("b", "blipp")
#Score("(cage) 3").reach(loop).post_sample("dopp", "KORGER1Samples")

test()