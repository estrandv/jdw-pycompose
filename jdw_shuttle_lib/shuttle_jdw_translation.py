from dataclasses import dataclass
from pythonosc.osc_message import OscMessage
from pythonosc.osc_packet import OscPacket
from shuttle_notation.parsing.element import ResolvedElement
from shuttle_notation.parsing.information_parsing import DynamicArg
from jdw_shuttle_lib.jdw_osc_utils import SC_DELAY_MS, create_msg
import jdw_shuttle_lib.note_utils as note_utils
from enum import Enum
from pretty_midi import note_number_to_hz

from line_classify import begins_with

# Applies JDW rules to Shuttle-data in order to determine the corresponding message type and contents for any given Element

class MessageType(Enum):
    PLAY_SAMPLE = 0
    NOTE_MOD = 1
    DRONE = 2
    EMPTY = 3
    IGNORE = 4
    NOTE_ON_TIMED = 5
    LOOP_START_MARKER = 6

def is_symbol(element: ResolvedElement, sym: str) -> bool:
    return element.suffix.lower() == sym \
        and element.prefix == "" \
        and element.index == 0

def resolve_external_id(element: ResolvedElement) -> str:
    resolved = element.suffix
    return resolved if resolved != "" else "id_" + str(element.index)

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
        extra = (12 * (octave - 1)) if octave > 0 else 0
        new_index = letter_check + extra

        return note_number_to_hz(new_index)

def args_as_osc(raw_args: dict[str, DynamicArg], override: list[str | float]):
    osc_args: list[str | float] = []

    for arg in override:
        osc_args.append(arg)

    for arg in raw_args:
        if arg not in osc_args:
            osc_args.append(arg)
            osc_args.append(float(raw_args[arg].value))
    return osc_args


# Contains the original element and the message it was resolved as
@dataclass
class ElementMessage:
    element: ResolvedElement
    osc: OscMessage

    def get_time(self) -> str:
        return str(self.element.args["time"]) if "time" in self.element.args else "0.0"

# Some elements have symbols or other syntax that force a certain osc format
def resolve_special_message(element: ResolvedElement, instrument_name: str) -> ElementMessage | None:
    if begins_with(element.suffix, "@"):
        # Remove symbol from suffix to create note mod external id
        return ElementMessage(element, to_note_mod(element, cut_first(element.suffix, 1)))
    elif is_symbol(element, "x"):
        # Silence
        return ElementMessage(element, create_msg("/empty_msg", []))
    elif is_symbol(element, "."):
        # Ignore
        pass
    elif is_symbol(element, "§"):
        # Loop start marker
        return ElementMessage(element, create_msg("/loop_started", []))
    elif begins_with(element.suffix, "$"):
        # Drone, note that suffix is trimmed similar to for note mod
        return ElementMessage(element, to_note_on(element, instrument_name, cut_first(element.suffix, 1)))

    return None

# TODO: Idea is to have each of these here and skip wrapper entirely
# See conversion methods in jdw_osc_utils - empty and marker only ones left but they can be elsewhere
def to_note_mod(element: ResolvedElement, external_id_override: str = "") -> OscMessage:
    external_id = resolve_external_id(element) if external_id_override == "" else external_id_override
    osc_args = args_as_osc(element.args, ["freq", resolve_freq(element)])
    return create_msg("/note_modify", [external_id, SC_DELAY_MS] + osc_args)

def to_note_on_timed(element: ResolvedElement, instrument_name: str) -> OscMessage:
    freq = resolve_freq(element)
    external_id = resolve_external_id(element)
    gate_time = str(element.args["sus"])
    osc_args = args_as_osc(element.args, ["freq", freq])
    return create_msg("/note_on_timed", [instrument_name, external_id, gate_time, SC_DELAY_MS] + osc_args)

def to_play_sample(element: ResolvedElement, instrument_name: str) -> OscMessage:
    osc_args = args_as_osc(element.args, ["freq", resolve_freq(element)])
    return create_msg("/play_sample", [
        resolve_external_id(element), instrument_name, element.index, element.prefix, SC_DELAY_MS
    ] + osc_args)

def to_note_on(element: ResolvedElement, instrument_name: str, external_id_override: str = "") -> OscMessage:
    external_id = resolve_external_id(element) if external_id_override == "" else external_id_override
    freq = resolve_freq(element)
    osc_args = args_as_osc(element.args, ["freq", freq])
    return create_msg("/note_modify", [external_id, SC_DELAY_MS] + osc_args)

# TODO: Trying to move away from this, slowly - hence the duplicates above
# Remove once nothing uses it anymore
@dataclass
class ElementWrapper:
    element: ResolvedElement
    instrument_name: str
    default_message_type: MessageType

    def args_as_osc(self, override: list = []) -> list:

        osc_args = []
        for arg in override:
            osc_args.append(arg)

        for arg in self.element.args:
            if arg not in osc_args:
                osc_args.append(arg)
                osc_args.append(float(self.element.args[arg]))
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

            return note_number_to_hz(new_index)
