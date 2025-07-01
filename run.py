import billboard_running as song
import sys
import uuid

from jdw_billboarding.lib import jdw_osc_utils

BBD_ROOT = "/home/estrandv/programming/jdw-pycompose/songs/"
#BBD_FILE = "rattlesnake.bbd"
#BBD_FILE = "courtRide.bbd"
#BBD_FILE = "arena.bbd"
#BBD_FILE = "been.bbd"
#BBD_FILE = "windyCity2.bbd"
#BBD_FILE = "larp.bbd"
#BBD_FILE = "trumpets.bbd"
BBD_FILE = "tmp.bbd"
#BBD_FILE = "lab.bbd"
#BBD_FILE = "vidya.bbd"
#BBD_FILE = "lighthouse.bbd"
#BBD_FILE = "gong.bbd"

def beep(amp = 1.0):
    song.default_client().send(jdw_osc_utils.create_msg("/note_on_timed", [
            "blip", # SynthDef to use, see load call above
            "beep-" + str(uuid.uuid4()), # Arbitrary unique external id for the ringing note
            "0.25", # Gate time ("note off after n sec")
            0, # Delay execution by time
            "freq", # Named args continue from here
            875.0,
            "relT",
            0.2,
            "amp",
            amp
        ]))

if "--update" in sys.argv:
    if ".bbd" in sys.argv[1]:
        song.configure(sys.argv[1])
    else:
        song.configure(BBD_ROOT + BBD_FILE)

    beep(0.1)

elif "--stop" in sys.argv:
    song.quiet(BBD_ROOT + BBD_FILE)

elif "--setup" in sys.argv:
    song.setup(BBD_ROOT + BBD_FILE)
    song.configure(BBD_ROOT + BBD_FILE)
    beep()

elif "--nrt" in sys.argv:
    song.nrt_record(BBD_ROOT + BBD_FILE)
else:
    if ".bbd" in sys.argv[1]:
        song.update_queue(sys.argv[1])
    else:
        song.update_queue(BBD_ROOT + BBD_FILE)
