from enum import Enum
from shuttle_notation import ResolvedElement
import note_utils
from pretty_midi import note_number_to_hz

class MessageType(Enum):
    DEFAULT = 0
    NOTE_MOD = 1
    DRONE = 2
    EMPTY = 3

def _is_empty_element(element: ResolvedElement):
    return element.suffix == "." \
        and element.prefix == "" \
        and element.index == 0 \
        and len(element.args) == 0

def resolve_message_type(element: ResolvedElement) -> MessageType:
    if element.suffix != "":
        if element.suffix[0] == "@":
            return MessageType.NOTE_MOD
        elif _is_empty_element(element):
            return MessageType.EMPTY
        elif element.suffix[0] == "$":
            return MessageType.DRONE
    return MessageType.DEFAULT 

def resolve_freq(element: ResolvedElement) -> float:
    if "freq" in element.args:
        return float(element.args["freq"])
    
    letter_check = note_utils.note_letter_to_midi(element.prefix)

    if letter_check == -1:

        # Placeholders 
        octave = 3

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
