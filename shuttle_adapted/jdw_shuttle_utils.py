from enum import Enum
from shuttle_notation import ResolvedElement

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