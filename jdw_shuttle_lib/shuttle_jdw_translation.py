from dataclasses import dataclass
from shuttle_notation import ResolvedElement
import jdw_shuttle_lib.note_utils as note_utils
from enum import Enum
from pretty_midi import note_number_to_hz

# Applies JDW rules to Shuttle-data in order to determine the corresponding message type and contents for any given Element

class MessageType(Enum):
    PLAY_SAMPLE = 0
    NOTE_MOD = 1
    DRONE = 2
    EMPTY = 3
    IGNORE = 4
    NOTE_ON_TIMED = 5
    LOOP_START_MARKER = 6

@dataclass
class ElementWrapper:
    element: ResolvedElement
    instrument_name: str
    default_message_type: MessageType

    def args_as_osc(self, override: list = []) -> list:
        
        osc_args = override
        for arg in self.element.args:
            if arg not in override:
                override.append(arg)
                override.append(float(self.element.args[arg]))
        return osc_args

    def is_symbol(self, sym: str) -> bool:
        element = self.element
        return element.suffix.lower() == sym \
            and element.prefix == "" \
            and element.index == 0 

    def resolve_external_id(self) -> str:
        element = self.element
        msg_type = self.resolve_message_type()

        resolved = "" 

        if msg_type != MessageType.NOTE_MOD:
            resolved = element.suffix
        else:
            # Remove the starter symbol denoting mod type 
            if len(element.suffix) > 1:
                resolved = "".join(element.suffix[1:])

        return resolved if resolved != "" else "id_" + str(element.index)

    def resolve_message_type(self) -> MessageType:
        
        element = self.element
        
        if element.suffix != "":
            if element.suffix[0] == "@":
                return MessageType.NOTE_MOD
            elif self.is_symbol("x"):
                return MessageType.EMPTY
            elif self.is_symbol("."):
                return MessageType.IGNORE
            elif self.is_symbol("§"):
                return MessageType.LOOP_START_MARKER
            elif element.suffix[0] == "$":
                return MessageType.DRONE
        return self.default_message_type 

    def resolve_freq(self) -> float:

        element = self.element

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
            extra = (12 * (octave - 1)) if octave > 0 else 0
            new_index = letter_check + extra

            print("DEBUG: Resolved note number", new_index, "from", element.prefix, element.index)

            return note_number_to_hz(new_index)

