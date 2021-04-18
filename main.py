from scales import *
from random import randint
from sheet import *

cmp = Composer()
padder = cmp.reg(MetaSheet("padder", "blipp", PostingTypes.PROSC))
blipp = cmp.reg(MetaSheet("bass", "blipp", PostingTypes.PROSC))
blipp2 = cmp.reg(MetaSheet("bass_assist", "blipp", PostingTypes.PROSC))
warsaw = cmp.reg(MetaSheet("warsaw", "warsawBass", PostingTypes.PROSC))
warsaw2 = cmp.reg(MetaSheet("warsaw2", "warsawBass", PostingTypes.PROSC))
moog = cmp.reg(MetaSheet("moog", "moogBass", PostingTypes.PROSC))
moog2 = cmp.reg(MetaSheet("moog2", "moogBass", PostingTypes.PROSC))
yamaha = cmp.reg(MetaSheet("yamaha", "YHDX200", PostingTypes.SAMPLE))
yamaha2 = cmp.reg(MetaSheet("yamaha2", "YHDX200", PostingTypes.SAMPLE))
korger = cmp.reg(MetaSheet("korger", "KORGER1Samples", PostingTypes.SAMPLE))
korger2 = cmp.reg(MetaSheet("korger2", "KORGER1Samples", PostingTypes.SAMPLE))
simple_korg = cmp.reg(MetaSheet("simple_korg", "KORGER1", PostingTypes.SAMPLE))
longsaw = cmp.reg(MetaSheet("longsaw", "longsaw", PostingTypes.PROSC))
longsaw2 = cmp.reg(MetaSheet("longsaw2", "longsaw", PostingTypes.PROSC))
varsaw = cmp.reg(MetaSheet("varsaw1", "varsaw", PostingTypes.PROSC))
varsaw2 = cmp.reg(MetaSheet("varsaw2", "varsaw", PostingTypes.PROSC))
sinepad = cmp.reg(MetaSheet("sinepad1", "sinepad", PostingTypes.PROSC))
rhodes = cmp.reg(MetaSheet("FMRhodes1", "FMRhodes1", PostingTypes.PROSC))
borch = cmp.reg(MetaSheet("BorchBattery", "BorchBattery", PostingTypes.MIDI))
drsix = cmp.reg(MetaSheet("drsix", "DR660", PostingTypes.SAMPLE))


rhodes.sheet("0 3 2 4 3", MAJOR, 5).all(">20 =10 #15").part_step([3,4], "=05 >15 #16")
rhodes.cont(3)

cmp.smart_sync()

# 30 05 30 05 05 05 30
longsaw.sheet("0 0 2 4 0 2 5 4 3", MAJOR, 6).all(">20 =05 #06").part_step([1, 4, 7], ">35 =30")
rhodes.cont(7)

cmp.smart_sync()

rhodes.cont(4)
korger2.sheet("24", CHROMATIC, 0).all("=025 #06")
korger.sheet("39 36 35 36 36", CHROMATIC, 0).all("=05 #05").part_step([1,2], "=025, #03")
cmp.smart_sync([korger2])

rhodes.cont(4)
longsaw.cont()
yamaha.sheet("19", CHROMATIC, 0).all("=10 #20 >40")
warsaw.sheet("0 0 0 4 . 0 0 0 2", MAJOR, 4).all("=025 >10 #10")

cmp.smart_sync([yamaha])


moog.sheet("2 3 2 5 2 3 2 0", MAJOR, 7).all("=40 >45 #05")
longsaw.cont()
rhodes.cont()
warsaw.cont()

cmp.smart_sync() 

yamaha.sheet("0", CHROMATIC, 0).all("=10")
#korger.sheet("39 36", CHROMATIC, 0).all("=05 #05")
cmp.cont([longsaw, rhodes, warsaw, korger]).smart_sync()

korger2.sheet("24", CHROMATIC, 0).all("=025 #06")
cmp.cont([longsaw, rhodes, warsaw, korger, moog]).smart_sync([korger2])


cmp.post_all()
