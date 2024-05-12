# Convenience script for easy system keybind access
from pythonosc import osc_message_builder, udp_client, osc_bundle_builder
import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils


client = udp_client.SimpleUDPClient("127.0.0.1", 13339) # Router
#client = udp_client.SimpleUDPClient("127.0.0.1", 14441) # Sequencer, direct
client.send(jdw_osc_utils.create_msg("/hard_stop", []))