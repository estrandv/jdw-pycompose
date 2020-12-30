from rest_client import *
from scales import *
from score import Score

loop=8.0
bpm(120)

scale = MINOR

Score("([a~b!][b~b!]a- [d~d!]i[g~j!]b~ )~:2 5").reach(loop).scale(scale).post_prosc("b", "blipp")
Score("(a--- e---)~:3 4").reach(loop).scale(scale).post_prosc("c", "blipp")
Score("([a~:3b]x[d~:3b]x[e~:3b]x[c~:3b]x) 5").reach(loop).scale(scale).post_prosc("d", "longsaw")
Score("(a3a!!a![aaaa]) 2").reach(loop).post_sample("dopp", "KORGER1Samples")

#test()