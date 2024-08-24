# Rewrite of the billboarding library, focusing on less messy code at the end of the explorative phase

from dataclasses import dataclass
from enum import Enum

FILTER_HEADER: str = ">>> "
SYNTH_HEADER_HEADER: str = "@"
SELECTION_MARKER: str = "*"
EFFECT_DEF_HEADER: str = "€"
COMMENT_SYMBOL = "#"
COMMAND_SYMBOL = "/"

class BillboardLineType(Enum):
    COMMENT = 0 # Other types can also be commented; this is for raw information comments
    GROUP_FILTER = 1
    SYNTH_HEADER = 2
    TRACK_DEFINITION = 3
    EFFECT_DEFINITION = 4
    COMMAND = 5

@dataclass
class BillboardLine:
    content: str
    type: BillboardLineType

def is_commented(line: str):
    return "#" in line.strip() and line.strip()[0] == "#"

def decomment(line: str) -> str:
    return decomment("".join(line[1:])) if is_commented(line) else line

# Split by newline, treating backslash as line continuation
def line_split(source: str) -> list[str]:
    return [line.strip().replace("\t", " ").replace("    ", " ") for line in source.split("\n")]

def begins_with(source: str, beginning: str) -> bool:
    clean_source = source.strip()
    return len(clean_source) >= len(beginning) and "".join(clean_source[0:len(beginning)]) == beginning

# Return all lines unaltered and in order, classified for later parsing
def classify_lines(billboard_string: str) -> list[BillboardLine]:

    classified_lines: list[BillboardLine] = []

    tracks_started = False

    for line in line_split(billboard_string):

        # Peek into post-comment content, to allow detection of commented types
        decommented = decomment(line) if is_commented(line) else line

        if begins_with(decommented, FILTER_HEADER):
            classified_lines.append(BillboardLine(line, BillboardLineType.GROUP_FILTER))
        elif begins_with(decommented, SYNTH_HEADER_HEADER) or begins_with(decommented, SELECTION_MARKER):
            classified_lines.append(BillboardLine(line, BillboardLineType.SYNTH_HEADER))
            tracks_started = True
        elif begins_with(decommented, EFFECT_DEF_HEADER):
            classified_lines.append(BillboardLine(line, BillboardLineType.EFFECT_DEFINITION))
        elif tracks_started and decommented != "":
            classified_lines.append(BillboardLine(line, BillboardLineType.TRACK_DEFINITION))
        elif begins_with(decommented, COMMAND_SYMBOL):
            classify_lines.append(BillboardLine(line, BillboardLineType.COMMAND))
        elif begins_with(line, "#"):
            classified_lines.append(BillboardLine(line, BillboardLineType.COMMENT))
        elif line != "": # Ignore empty
            print("WARN: could not classify line", line)

    return classified_lines

# Tests
if __name__ == "__main__":

    # begins_with
    assert begins_with("#comment", "#")
    assert begins_with(">>> filter", ">>>")
    assert not begins_with(".>>>", ">>>")

    # is_commented
    assert is_commented("#@basic")
    assert is_commented("###")
    assert not is_commented("basic#")

    # classify_lines
    assert classify_lines(">>> hey")[0].type == BillboardLineType.GROUP_FILTER
    assert classify_lines("#>>> hey")[0].type == BillboardLineType.GROUP_FILTER
    assert classify_lines("    #>>> hey")[0].type == BillboardLineType.GROUP_FILTER
    assert classify_lines("    >>> hey")[0].type == BillboardLineType.GROUP_FILTER

    assert classify_lines("@synth")[0].type == BillboardLineType.SYNTH_HEADER
    assert classify_lines("*@synth")[0].type == BillboardLineType.SYNTH_HEADER
    assert classify_lines("# hello")[0].type == BillboardLineType.COMMENT
    assert classify_lines("€yeah")[0].type == BillboardLineType.EFFECT_DEFINITION
    assert classify_lines("@synth\nsomthing")[1].type == BillboardLineType.TRACK_DEFINITION
