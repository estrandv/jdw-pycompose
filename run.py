import songs.run_billboard as song 
import sys
import client 

import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils

BDD_FILE = "courtRide.bbd"
#BDD_FILE = "lab.bbd"
#BDD_FILE = "nrt_test.bbd"

if "--update" in sys.argv:
    song.configure(BDD_FILE) 
elif "--stop" in sys.argv:
    client.get_default().send(jdw_osc_utils.create_msg("/hard_stop", []))
    # Note that this kills any existing drones, which will have to be manually recreated 
    client.get_default().send_message("/note_modify", [
        "(.*)",
        0,
        "gate",
        0.0
    ])
elif "--nrt" in sys.argv:
    song.nrt_export(BDD_FILE)
else:
    # Gate stuff is there to sleep/wake any permanent drones 
    song.run(BDD_FILE)