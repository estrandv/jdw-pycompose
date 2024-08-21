from line_classify import BillboardLine, BillboardLineType, is_commented



# Returns only the first unbroken set of uncommented (commented does not break chain) group filters
def extract_group_filters(lines: list[BillboardLine]) -> list[list[str]]:
    full_set: list[list[str]] = []

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
    separated: list[list[BillboardLine]] = []

    for line in lines:
        if line.type == BillboardLineType.SYNTH_HEADER:
            if not is_commented(line.content):
                separated.append([line])
        elif len(separated) > 0:
            separated[-1].append(line)

    return separated

# Tests
if __name__ == "__main__":

    chunk_result = extract_synth_chunks([
        BillboardLine("ignored", BillboardLineType.TRACK_DEFINITION),
        BillboardLine("synth", BillboardLineType.SYNTH_HEADER),
        BillboardLine("track", BillboardLineType.TRACK_DEFINITION),
        BillboardLine("#synth", BillboardLineType.SYNTH_HEADER),
        BillboardLine("effect", BillboardLineType.EFFECT_DEFINITION),
        BillboardLine("synth", BillboardLineType.SYNTH_HEADER),
        BillboardLine("comment", BillboardLineType.COMMENT),
    ])

    assert len(chunk_result) == 2, "Should have 2 synth chunks: " + str(chunk_result)
    assert len(chunk_result[0]) == 3, "First synth chunk should have 3 included lines: " + str(chunk_result[0])
