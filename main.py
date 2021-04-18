from rest_client import *
from scales import *
from score import Score
from random import randint
import pscore
from composer import PostingTypes
from sheet import *

cmp = Composer()
padder = cmp.reg(MetaSheet("padder", "blipp", PostingTypes.PROSC))
blipp = cmp.reg(MetaSheet("bass", "blipp", PostingTypes.PROSC))
blipp2 = cmp.reg(MetaSheet("bass_assist", "blipp", PostingTypes.PROSC))
warsaw = cmp.reg(MetaSheet("warsaw", "warsawBass", PostingTypes.PROSC))
warsaw2 = cmp.reg(MetaSheet("warsaw2", "warsawBass", PostingTypes.PROSC))
moog = cmp.reg(MetaSheet("moog", "moogBass", PostingTypes.PROSC))
moog2 = cmp.reg(MetaSheet("moog2", "moogBass", PostingTypes.PROSC))
yamaha = cmp.reg(MetaSheet("drum", "YHDX200", PostingTypes.SAMPLE))
yamaha2 = cmp.reg(MetaSheet("drum4", "YHDX200", PostingTypes.SAMPLE))
korger = cmp.reg(MetaSheet("drum2", "KORGER1Samples", PostingTypes.SAMPLE))
korger2 = cmp.reg(MetaSheet("drum3", "KORGER1Samples", PostingTypes.SAMPLE))
simple_korg = cmp.reg(MetaSheet("simple_korg", "KORGER1", PostingTypes.SAMPLE))
longsaw = cmp.reg(MetaSheet("lead", "longsaw", PostingTypes.PROSC))
longsaw2 = cmp.reg(MetaSheet("lead2", "longsaw", PostingTypes.PROSC))
varsaw = cmp.reg(MetaSheet("varsaw1", "varsaw", PostingTypes.PROSC))
varsaw2 = cmp.reg(MetaSheet("varsaw2", "varsaw", PostingTypes.PROSC))
sinepad = cmp.reg(MetaSheet("sinepad1", "sinepad", PostingTypes.PROSC))
rhodes = cmp.reg(MetaSheet("FMRhodes1", "FMRhodes1", PostingTypes.PROSC))
borch = cmp.reg(MetaSheet("BorchBattery", "BorchBattery", PostingTypes.MIDI))
drsix = cmp.reg(MetaSheet("drsix", "DR660", PostingTypes.SAMPLE))

#bpm(140)

#moog.sheet("0 3 0 4 . 0 3 0 5", MAJOR, 6).all("=10 >10 #10").part_step([1], "=20 >20 chorus03").part_step([2,4], "=05 >20")
yamaha.sheet("1 4 1 8 . 1 4 17 8", CHROMATIC, 0).part_step([1,3], "#35")
yamaha2.sheet("31 31 12 12 31 31 14 14 . 31 31 18 18 31 31 22 22 ", CHROMATIC, 0).all("=05")
drsix.sheet("35 28", CHROMATIC, 0).all("#30 =40")
sinepad.sheet("0 2 4 2", MAJOR, 8)
#moog.sheet("1 4 2 2 4", MINOR, 5).all("=20 >30").part_step([3,4], "=10")
#blipp.sheet("1 2 1 2 1 4 1 4", MINOR, 7).all("=05 >10")

#drsix.sheet("0 5 18 3 1. 14 80 19 43 41", CHROMATIC, 0).all("=05 >10 #10").part_step([3,4], "=025 #08")
# TODO: This goes out of rane for the part step 4 thingie. 
#rhodes.sheet("1 1 1 2. 3 3 3 2", MAJOR, 6).all("=05 >20 #80").part_step([4], "=25 >25")
#warsaw.sheet("0 ", MAJOR, 5).all("=40 >80 #05").on_note([1], "#0")

#cmp.sync()


cmp.post_all()
