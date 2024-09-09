import billboard_running as song
import sys

import jdw_osc_utils

BDD_ROOT = "/home/estrandv/programming/jdw-pycompose/songs/"
BDD_FILE = "courtRide.bbd"
#BDD_FILE = "lab.bbd"
#BDD_FILE = "nrt_test.bbd"

if "--update" in sys.argv:
    song.configure(BDD_ROOT + BDD_FILE)
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
    song.setup(BDD_ROOT + BDD_FILE)

elif "--nrt" in sys.argv:
    song.nrt_record(BDD_ROOT + BDD_FILE)
else:
    song.configure(BDD_ROOT + BDD_FILE)
    song.update_queue(BDD_ROOT + BDD_FILE)
