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
organReed = cmp.reg(MetaSheet("organReed1", "organReed", PostingTypes.PROSC))
chaoscillator = cmp.reg(MetaSheet("chaos1", "chaoscillator", PostingTypes.PROSC))
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

# TODO: taggable sheets like sheet("0a 0a 1b 2b").tag("b", "=05 >05")
# Could be expanded to cmp level, so that there are "global tags", or just by metadata
# Another approach is to allow in-line attributes like sheet("0 2 3(=05 >20) 4"), which is a little messier but nice for shorthand 

yamaha.sheet("79 28").all("=80 >05")
rhodes.sheet("2 3 2 2 5 6 5 7 5 3 4 2", MINOR, 7).all(">20").dots([3,7], "=35").dots([1,2,4,5], "=05")
drsix.sheet("26 26 26 26 . 26 26 26 12")
korger.sheet("8 7 8 9").all("#30 >05 =20").dots([1,3], "=05").dots([2,4], "=15")
warsaw.sheet("0 2 0 3 . 0 2 4 3 . 0 2 0 3 . 0 2 1 0", MINOR, 7).all("=20 >40 #03")
#longsaw.sheet("2 4 6 4 6 4 6 4 . 3 4 6 4 6 4 6 4", MINOR, 5).all("=025 >0")
#chaoscillator.sheet("0 1 0 3 0 . 0 1 3 4 1 . 4 1 0 3 0 . 1 2 3 4 0", MINOR, 6).all("=05 >20").dots([3,4], "=025")
#rhodes.sheet("4 4 4 6 . 4 4 2 6 . 4 5 3 6 . 4 4 2 6", MINOR, 5).all(">10 #40 =025")

cmp.smart_sync([varsaw])

cmp.post_all()
