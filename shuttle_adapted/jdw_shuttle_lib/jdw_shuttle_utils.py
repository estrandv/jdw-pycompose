# utilities for interpreting shuttle notation according to the jackdaw standard 

from enum import Enum
from shuttle_notation import ResolvedElement
import jdw_shuttle_lib.note_utils as note_utils
from pretty_midi import note_number_to_hz

class MessageType(Enum):
    DEFAULT = 0
    NOTE_MOD = 1
    DRONE = 2
    EMPTY = 3
    IGNORE = 4

def _is_empty_element(element: ResolvedElement):
    return element.suffix.lower() == "x" \
        and element.prefix == "" \
        and element.index == 0 

def _is_spacer_element(element: ResolvedElement):
    return element.suffix.lower() == "." \
        and element.prefix == "" \
        and element.index == 0 

def resolve_external_id(element: ResolvedElement) -> str:
    msg_type = resolve_message_type(element)

    resolved = "" 

    if msg_type != MessageType.NOTE_MOD:
        resolved = element.suffix
    else:
        # Remove the starter symbol denoting mod type 
        if len(element.suffix) > 1:
            resolved = "".join(element.suffix[1:])

    return resolved if resolved != "" else "NOID" 

def resolve_message_type(element: ResolvedElement) -> MessageType:
    if element.suffix != "":
        if element.suffix[0] == "@":
            return MessageType.NOTE_MOD
        elif _is_empty_element(element):
            return MessageType.EMPTY
        elif _is_spacer_element(element):
            return MessageType.IGNORE
        elif element.suffix[0] == "$":
            return MessageType.DRONE
    return MessageType.DEFAULT 

def resolve_freq(element: ResolvedElement) -> float:
    if "freq" in element.args:
        return float(element.args["freq"])
    
    letter_check = note_utils.note_letter_to_midi(element.prefix)

    if letter_check == -1:

        # Placeholders 
        # TODO: Complete bullshit, but helps with keybaoard usage for now 
        #octave = 0 if element.index > 12 else 3
        octave = 0

        extra = (12 * (octave + 1)) if octave > 0 else 0
        new_index = element.index + extra
        # TODO: port transpose from scales.py 
        #   Implied scale: Chromatic 
        #scale = scales.MAJOR
        #new_index = transpose(new_index, scale)
        freq = note_number_to_hz(new_index)
        return freq 

    else:
        # E.g. "C" or "C#" or "Cb"
        letter_and_semitone = element.prefix.lower() 
        # As in the "3" of "c3"
        octave = element.index if element.index != None else 1

        # Math, same as for index freq calculation
        extra = (12 * (octave + 1)) if octave > 0 else 0
        new_index = letter_check + extra

        return note_number_to_hz(new_index)
