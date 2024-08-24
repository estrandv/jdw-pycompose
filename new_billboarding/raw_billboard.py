from line_classify import *
from filtering import is_commented
from dataclasses import dataclass
from parsing import *

@dataclass
class SynthSection:
    header: SynthHeader
    tracks: list[TrackDefinition]
    effects: list[EffectDefinition]

@dataclass
class RawBillboard:
    group_filters: list[list[str]]
    synth_sections: list[SynthSection]

def create(group_filters: list[list[str]], synth_chunks: list[list[BillboardLine]]) -> RawBillboard:

    synth_sections: list[SynthSection] = []
    for chunk in synth_chunks:
        assert len(chunk) > 0, "Malformed synth chunk: no content"
        assert chunk[0].type == BillboardLineType.SYNTH_HEADER, "Malformed synth chunk; does not start with synth header"

        synth_header_content = chunk[0].content.strip()
        header = parse_synth_header(synth_header_content)

        tracks: list[TrackDefinition] = []
        effects: list[EffectDefinition] = []
        track_counter = 0
        for line in chunk[1:] if len(chunk) > 1 else []:
            if line.type == BillboardLineType.TRACK_DEFINITION:
                if not is_commented(line.content.strip()):
                    track_definition = parse_track_definition(line.content.strip(), track_counter)
                    tracks.append(track_definition)
                # Count commented tracks, so that they retain their identifying index when commented
                track_counter += 1

            if line.type == BillboardLineType.EFFECT_DEFINITION:
                if not is_commented(line.content.strip()):
                    effect_definition = parse_effect_definition(line.content.strip())
                    effects.append(effect_definition)

        synth_sections.append(SynthSection(header, tracks, effects))

    return RawBillboard(group_filters, synth_sections)
