from pythonosc.osc_bundle import OscBundle
from shuttle_notation.parsing.element import ResolvedElement

from jdw_shuttle_lib import jdw_osc_utils
from jdw_shuttle_lib import shuttle_jdw_translation
from jdw_shuttle_lib.shuttle_jdw_translation import ElementWrapper, MessageType

def create_sequencer_notes(elements: list[ResolvedElement], synth_name: str, is_sample = False) -> list[OscBundle]:
    sequence: list[OscBundle] = []
    for element in elements:

        # TODO: See changes in shuttle_jdw_translation - bypass wrapper and start over
        #wrapper = ElementWrapper(element, synth_name, MessageType.PLAY_SAMPLE if is_sample else MessageType.NOTE_ON_TIMED)
        #msg = jdw_osc_utils.create_sequencer_note(wrapper)

        # TODO: Should determine which type of message dynamically, accounting for ignored message types
        msg = shuttle_jdw_translation.to_note_on_timed(element, synth_name)
        timed_msg_bundle = jdw_osc_utils.to_timed_osc(str(element.args["time"]), msg)
        sequence.append(timed_msg_bundle)

    return sequence
