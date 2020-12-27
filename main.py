from rest_client import *


# Score("cccc").stretch(8).post_prosc("b", "longsaw")

loop=8.0
bpm(60)

Score("M(a-e[.a]g-..)~:4 5").reach(loop).post_prosc("b", "blipp")
Score("M([ae]x[eg]x)~:4 6").reach(loop).post_prosc("bgg", "longsaw")
Score("M(e--- a-g-)~:3 4").reach(loop).post_prosc("cobb", "longsaw")
Score("(cage) 3").reach(loop).post_sample("dopp", "KORGER1Samples")