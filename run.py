import songs.run_billboard as song 
import sys
import client 

import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils

#BDD_FILE = "courtRide.bbd"
BDD_FILE = "lab.bbd"

if "--update" in sys.argv:
    song.configure(BDD_FILE) 
elif "--stop" in sys.argv:
    client.get_default().send(jdw_osc_utils.create_msg("/hard_stop", []))
else:
    song.run(BDD_FILE)