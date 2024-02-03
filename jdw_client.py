from osc_transform import SendType, create_msg, MessageWrapper, to_timed_osc
from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
import parsing
from pythonosc import udp_client
import uuid
from typing import List 


class JDWClient:
    def __init__(self):
        self.client = udp_client.SimpleUDPClient("127.0.0.1", 13339) # Router

    def set_sequencer_bpm(self, value: int):
        self.client.send(create_message("/set_bpm", [value]))

    def stop(self):
        self.client.send(create_msg("/hard_stop", []))

    def play(
        self,
        sc_synth_name: str,
        pycompose_script: str,
        external_id: str,
        default_send_type: SendType = SendType.NOTE_ON_TIMED
    ):
        parsed_messages: List[parsing.Message] = parsing.full_parse(pycompose_script)

        main_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        # NOTE: Meta-info for the update-queue command, mainly the external id of the sequencer 

        note_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        for wrapper in [MessageWrapper(msg) for msg in parsed_messages]:

            osc_msg = wrapper.to_osc(default_send_type, sc_synth_name)
            timed_osc_msg = to_timed_osc(wrapper.get_time(), osc_msg)
            note_bundle.add_content(timed_osc_msg)

        main_bundle.add_content(create_msg("/bundle_info", ["update_queue"]))
        main_bundle.add_content(create_msg("/update_queue_info", [external_id]))
        main_bundle.add_content(note_bundle.build())

        self.client.send(main_bundle.build())

    # TODO: somehow crashes on samples due to missing "index arg at 2th", investigate!
    def nrt_record(
        self,
        sc_synth_name: str,
        pycompose_script: str,
        external_id: str,
        default_send_type: SendType = SendType.NOTE_ON_TIMED,
        bpm: float = 120.0 # TODO: Fix when the expectation in jdw-sc is corrected
    ):

        parsed_messages: List[parsing.Message] = parsing.full_parse(pycompose_script)

        main_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

        note_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        
        timeline = 0
        for wrapper in [MessageWrapper(msg) for msg in parsed_messages]:

            osc_msg = wrapper.to_osc(default_send_type, sc_synth_name)
            timed_osc_msg = to_timed_osc(wrapper.get_time(), osc_msg)
            note_bundle.add_content(timed_osc_msg)
            timeline += float(wrapper.get_time())

        main_bundle.add_content(create_msg("/bundle_info", ["nrt_record"]))
        # TODO: BPM and project output 
        main_bundle.add_content(create_msg("/nrt_record_info", [bpm, "/home/estrandv/jdw_output/" + external_id + ".wav", timeline]))
        main_bundle.add_content(note_bundle.build())

        self.client.send(main_bundle.build())

    # TODO: Kinda dumb convenience method here while I figure out how I want to do scd reading 
    def read_custom_synths(self):
        with open("synthdefs/pycompose.scd", "r") as file:
            data = file.read() 
            self.client.send(create_msg("/read_scd", [data]))
