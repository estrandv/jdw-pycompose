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
nintendo = cmp.reg(MetaSheet("nintendo_soundfont1", "nintendo_soundfont", PostingTypes.MIDI, False))
nintendo2 = cmp.reg(MetaSheet("nintendo_soundfont2", "nintendo_soundfont", PostingTypes.MIDI, False))


cmp.smart_sync()

cmp.post_all()
