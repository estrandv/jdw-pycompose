# Meant to be broken down into smaller scripts once it takes shape

from line_classify import begins_with, BillboardLine, BillboardLineType, classify_lines
from dataclasses import dataclass

# TODO: Not really used here
def decomment(line: str):
    return decomment("".join(line[1:])) if is_commented(line) else line

def is_commented(line: str):
    return "#" in line.strip() and line.strip()[0] == "#"

# Returns only the first unbroken set of uncommented (commented does not break chain) group filters
def extract_group_filters(lines: list[BillboardLine]) -> list[list[str]]:
    full_set = []

    started = False
    for line in lines:

        if line.type == BillboardLineType.GROUP_FILTER:
            if not is_commented(line.content):
                full_set.append(line.content.split(" "))
        elif started:
            break # Only count the first unbroken chain of filters

    return full_set

# Returns billboard lines sorted by synth headers (each sublist containinng the header and the lines below it)
def extract_synth_chunks(lines: list[BillboardLine]) -> list[list[BillboardLine]]:
    separated = []

    for line in lines:
        if line.type == BillboardLineType.SYNTH_HEADER:
            separated.append([line])
        elif len(separated) > 0:
            separated[-1].append(line)

    return separated
