import billboard_running as song
import sys

from jdw_billboarding.lib import jdw_osc_utils

BBD_ROOT = "/home/estrandv/programming/jdw-pycompose/songs/"
BBD_FILE = "experiments.bbd"

if "--update" in sys.argv:
    song.configure(BBD_ROOT + BBD_FILE)
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

elif "--nrt" in sys.argv:
    song.nrt_record(BBD_ROOT + BBD_FILE)
else:
    song.update_queue(BBD_ROOT + BBD_FILE)
