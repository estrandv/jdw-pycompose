from dataclasses import dataclass
from pythonosc.osc_bundle import OscBundle

from shuttle_notation import Parser, ResolvedElement
from decimal import Decimal
from pythonosc import osc_message_builder, udp_client, osc_bundle_builder
from pythonosc.osc_packet import OscPacket

import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils
from jdw_shuttle_lib.shuttle_jdw_translation import ElementWrapper, MessageType


@dataclass
class Tracker(dict):
    parser = Parser() 
    bpm = 120.0 

    def into_nrt_record_bundles(self, zero_time_messages: list[OscPacket] = []) -> list[OscBundle]:

        bundles = []
        for track in self:

            # TODO: Enforce this key standard with custom setter and dataclass  
            name_split = track.split(":")
            track_id = name_split[0]
            synth_name = name_split[1]

            elements = self.parser.parse(self[track])

            # Append zero time messages before converting all sequences
            sequence = [jdw_osc_utils.to_timed_osc("0.0", msg) for msg in zero_time_messages] + create_notes(elements, synth_name)

            # Example nrt send 
            # TODO: Hardcodes, but fine for now since it's not public-facing 
            file_name = "/home/estrandv/jdw_output/track_" + track_id + ".wav"
            end_time = sum([float(e.args["time"]) for e in elements]) + 4.0 # A little extra 
            
            bundles.append(jdw_osc_utils.create_nrt_record_bundle(sequence, file_name, end_time, self.bpm))

        return bundles 

    # Creates a batch queue bundle to queue all mentioned tracks at once
    def into_sequencer_queue_bundle(self, stop_missing = True) -> OscBundle:
        
        bundles = self.into_sequencer_queue_bundles() 
        return jdw_osc_utils.create_batch_queue_bundle(bundles, stop_missing)

    def into_sequencer_queue_bundles(self) -> list[OscBundle]:
        bundles = []
        for track in self:

            name_split = track.split(":")
            track_id = name_split[0]
            synth_name = name_split[1]

            elements = self.parser.parse(self[track])

            sequence = create_notes(elements, synth_name)
            
            bundles.append(jdw_osc_utils.create_queue_update_bundle(track_id, sequence))

        return bundles 

def create_notes(elements: list[ResolvedElement], synth_name) -> list[OscBundle]:
    sequence = []
    for element in elements:

        is_sample = False 
        resolved_name = synth_name
        # TODO: Also not an enforced standard 
        if len(synth_name) >= 3 and "SP_" in synth_name:
            first_letters = "".join(synth_name[0:3])
            if first_letters == "SP_":
                is_sample = True 
                resolved_name = "".join(synth_name[3:])

        wrapper = ElementWrapper(element, resolved_name, MessageType.PLAY_SAMPLE if is_sample else MessageType.NOTE_ON_TIMED)
        
        msg = jdw_osc_utils.create_jdw_note(wrapper)

        if msg != None:
            sequence.append(msg)

    return sequence

### TODO: Billboard stuff below, placing here for convenience, might replace tracker altogether

from billboarding import *

def create_notes_b(elements: list[ResolvedElement], synth_name, is_sample = False) -> list[OscBundle]:
    sequence = []
    for element in elements:

        wrapper = ElementWrapper(element, synth_name, MessageType.PLAY_SAMPLE if is_sample else MessageType.NOTE_ON_TIMED)
        
        msg = jdw_osc_utils.create_jdw_note(wrapper)

        if msg != None:
            sequence.append(msg)

    return sequence

def create_sequencer_queue_bundles(tracks: dict[str,BillboardTrack]) -> list[OscBundle]:
    bundles = []
    for track_name in tracks:
        track = tracks[track_name]

        sequence = create_notes_b(track.elements, track.synth_name, track.is_sampler)
        
        bundles.append(jdw_osc_utils.create_queue_update_bundle(track_id, sequence))

    return bundles 

# Creates a batch queue bundle to queue all mentioned tracks at once
def create_sequencer_queue_bundle(tracks: dict[str,BillboardTrack], stop_missing = True) -> OscBundle:
    
    bundles = create_sequencer_queue_bundles(tracks)
    return jdw_osc_utils.create_batch_queue_bundle(bundles, stop_missing)