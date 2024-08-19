# Rewrite of the billboarding library, focusing on less messy code at the end of the explorative phase

from dataclasses import dataclass
from enum import Enum

FILTER_HEADER: str = ">>> "
SYNTH_HEADER_HEADER: str = "@"
EFFECT_DEF_HEADER: str = "€"
COMMENT_SYMBOL = "#"

class BillboardLineType(Enum):
    COMMENT = 0 # Other types can also be commented; this is for raw information comments
    GROUP_FILTER = 1
    SYNTH_HEADER = 2
    TRACK_DEFINITION = 3
    EFFECT_DEFINITION = 4

@dataclass
class BillboardLine:
    content: str
    type: BillboardLineType

# Split by newline, treating backslash as line continuation
def line_split(source: str) -> list[str]:
    return [line.strip().replace("\t", " ").replace("    ", " ") for line in source.split("\n")]

# TODO: Test that indices align
def begins_with(source: str, beginning: str) -> bool:
    return len(source) >= len(beginning) and "".join(source[0:len(beginning)]) == beginning

# Return all lines unaltered and in order, classified for later parsing
def classify_lines(billboard_string: str) -> list[BillboardLine]:

    classified_lines: list[BillboardLine] = []

    tracks_started = False

    for line in line_split(billboard_string):

        # Peek into post-comment content, to allow detection of commented types
        decommented = "".join(line.split(COMMENT_SYMBOL)[1:]) if begins_with(line, COMMENT_SYMBOL) else line

        # Check if whole line is a comment
        current_is_commented = begins_with(line, COMMENT_SYMBOL)

        if begins_with(decommented, FILTER_HEADER):
            classified_lines.append(BillboardLine(line, BillboardLineType.GROUP_FILTER))
        elif begins_with(decommented, SYNTH_HEADER_HEADER):
            classified_lines.append(BillboardLine(line, BillboardLineType.SYNTH_HEADER))
            tracks_started = True
        elif begins_with(decommented, EFFECT_DEF_HEADER):
            classified_lines.append(BillboardLine(line, BillboardLineType.EFFECT_DEFINITION))
        elif tracks_started and decommented != "":
            classified_lines.append(BillboardLine(line, BillboardLineType.TRACK_DEFINITION))
        else:
            print("WARN: could not classify line", line)

    return classified_lines
