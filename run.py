import billboard_running as song
import sys

from jdw_billboarding.lib import jdw_osc_utils

BBD_ROOT = "/home/estrandv/programming/jdw-pycompose/songs/"
#BBD_FILE = "rattlesnake.bbd"
#BBD_FILE = "arena.bbd"
#BBD_FILE = "been.bbd"
#BBD_FILE = "windyCity.bbd"
#BBD_FILE = "larp.bbd"
BBD_FILE = "lab.bbd"
#BBD_FILE = "vidya.bbd"

def beep():
    song.default_client().send(jdw_osc_utils.create_msg("/note_on_timed", [
            "blip", # SynthDef to use, see load call above
            "confirmation_beep", # Arbitrary unique external id for the ringing note
            "0.25", # Gate time ("note off after n sec")
            0, # Delay execution by time
            "freq", # Named args continue from here
            275.0,
            "relT",
            0.2
        ]))

if "--update" in sys.argv:
    song.configure(BBD_ROOT + BBD_FILE)
    #beep()

elif "--stop" in sys.argv:
    song.quiet(BBD_ROOT + BBD_FILE)

elif "--setup" in sys.argv:
    song.setup(BBD_ROOT + BBD_FILE)
    song.configure(BBD_ROOT + BBD_FILE)
    beep()

elif "--nrt" in sys.argv:
    song.nrt_record(BBD_ROOT + BBD_FILE)
else:
    song.update_queue(BBD_ROOT + BBD_FILE)
