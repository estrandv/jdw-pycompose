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
yamaha = cmp.reg(MetaSheet("yamaha", "YHDX200", PostingTypes.SAMPLE, False))
yamaha2 = cmp.reg(MetaSheet("yamaha2", "YHDX200", PostingTypes.SAMPLE, False))
korger = cmp.reg(MetaSheet("korger", "KORGER1Samples", PostingTypes.SAMPLE, False))
korger2 = cmp.reg(MetaSheet("korger2", "KORGER1Samples", PostingTypes.SAMPLE, False))
simple_korg = cmp.reg(MetaSheet("simple_korg", "KORGER1", PostingTypes.SAMPLE, False))
longsaw = cmp.reg(MetaSheet("longsaw", "longsaw", PostingTypes.PROSC))
longsaw2 = cmp.reg(MetaSheet("longsaw2", "longsaw", PostingTypes.PROSC))
varsaw = cmp.reg(MetaSheet("varsaw1", "varsaw", PostingTypes.PROSC))
varsaw2 = cmp.reg(MetaSheet("varsaw2", "varsaw", PostingTypes.PROSC))
sinepad = cmp.reg(MetaSheet("sinepad1", "sinepad", PostingTypes.PROSC))
rhodes = cmp.reg(MetaSheet("FMRhodes1", "FMRhodes1", PostingTypes.PROSC))
borch = cmp.reg(MetaSheet("BorchBattery", "BorchBattery", PostingTypes.MIDI))
drsix = cmp.reg(MetaSheet("drsix", "DR660", PostingTypes.SAMPLE, False))
nintendo = cmp.reg(MetaSheet("nintendo_soundfont1", "nintendo_soundfont", PostingTypes.MIDI, False))
nintendo2 = cmp.reg(MetaSheet("nintendo_soundfont2", "nintendo_soundfont", PostingTypes.MIDI, False))


varsaw.sheet("0 4 0 2", MAJOR, 8).all("=10 >10 #06 att005")
warsaw.sheet("0 0 0 0 0 0 0 0 2 2 2 2 2 2 2 2 1 1 1 1 1 1 1 1 3 3 3 3 3 3 3 3", MAJOR, 5).all("=05 >10 att05")
#blipp.sheet("0 3 0 2 . 2 3 4 3 . 4 6 7 5 . 2 3 4 5", MAJOR, 7).all("=05").part_step([4], "=20 >40")
#drsix.sheet("0 4 15 17 0 4", CHROMATIC, 0).all("=10").part_step([3,4], "=025").part_step([5], "=05")
moog.sheet("0 6 3 8", MAJOR, 6).all("=40 >40 #05")
#yamaha.sheet("0", CHROMATIC, 0).all("=20 pan08 #08")
longsaw.sheet("0 1 2 0 . 0 1 3 0 . 0 1 0 0 . 0 1 4 0", MAJOR, 6).all("=05 >20 #05")

#:drsix.sheet("8 7 66 56", CHROMATIC, 0).all("=10 att004").part_step([1,2], "=05").part_step([4], "=20")
yamaha.sheet("48").all("=05 att002")
cmp.smart_sync()
#cmp.smart_sync([blipp])

cmp.post_all()
