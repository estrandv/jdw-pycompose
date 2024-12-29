import billboard_running as song
import sys

from jdw_billboarding.lib import jdw_osc_utils

BBD_ROOT = "/home/estrandv/programming/jdw-pycompose/songs/"
BBD_FILE = "rattlesnake.bbd"

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
    beep()

elif "--stop" in sys.argv:
    song.default_client().send(jdw_osc_utils.create_msg("/hard_stop", []))
    # Note that this kills any existing drones, which will have to be manually recreated
    song.default_client().send_message("/note_modify", [
        "(.*)",
        0,
        "gate",
        0.0
    ])
    # TODO: Make setup separate
    song.setup(BBD_ROOT + BBD_FILE)
    beep()

elif "--nrt" in sys.argv:
    song.nrt_record(BBD_ROOT + BBD_FILE)
else:
    song.update_queue(BBD_ROOT + BBD_FILE)
