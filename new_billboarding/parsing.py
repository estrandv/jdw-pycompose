from line_classify import *
from dataclasses import dataclass

@dataclass
class EffectDefinition:
    instrument_name: str
    unique_suffix: str
    args_string: str

@dataclass
class TrackDefinition:
    content: str
    group_override: str
    arg_override: str
    index: int

@dataclass
class SynthHeader:
    instrument_name: str
    is_done: bool
    is_sampler: bool
    is_selected: bool
    default_args_string: str
    additional_args_string: str


# TODO: Untested
def cut_first(source: str, amount: int) -> str:
    return "".join(source[amount:]) if len(source) >= amount else ""

def parse_effect_definition(content: str):

    space_split = content.split(" ")
    # Cut off the "€ or ¤"
    core_part = cut_first(space_slot[0], 1)

    assert ":" in core_part, "Must provide a unique id for effect, e.g. " + core_part + ":myId"

    effect_type = core_part.split(":")[0]
    unique_suffix = core_part.split(":")[1]
    arg_string = space_split[1] if len(space_split) > 1 else ""

    # e.g. reverb_mygroup_3
    # or reverb_mygroup_a if effect was listed as reverb:a
    #external_id = effect_type + "_" + current_group_name + "_" + unique_suffix
    return EffectDefinition(effect_type, unique_suffix, arg_string)

def parse_track_definition(content: str, index: int) -> TrackDefinition:

    arg_override = ""
    group_override = ""
    track_data = content

    # Handle meta data as <group_name;arg_override>
    if content[0] == "<" and ">" in content:
        assert not ("€" in content), "€-notation can not be used in tandem with <>-overriding"
        track_data = "".join(content.split(">")[1:])
        # Between <...>
        meta_data = "".join(content.split(">")[0][1:])

        # Handle meta_data as <group_name;args>
        meta_split = meta_data.split(";")
        group_override = meta_split[0]

        arg_override = meta_split[1] if len(meta_split) > 1 else ""

    return TrackDefinition(track_data, group_override, arg_override, index)

def parse_synth_header(content: str) -> SynthHeader:

        # Expect format: @synth_name:group_name args (pads)
        space_split = content.split(" ")

        # Cut off the "@" and any eventual "*"
        is_selected = False
        id_string = cut_first(space_split[0], 1)
        if begins_with(space_split[0], "*@"):
            id_string = cut_first(space_split[0], 2)
            is_selected = True

        instrument_name = id_string.split(":")[0] if ":" in id_string else id_string
        current_group_name = id_string.split(":")[1] if ":" in id_string else ""

        current_default_args_string = space_split[1] if len(space_split) > 1 else ""
        # E.g. pads configuration for SP
        additional_config_string = space_split[2] if len(space_split) > 2 else ""
        current_is_sampler = False
        current_is_drone = False

        if begins_with(instrument_name, "SP_"):
            instrument_name = cut_first(instrument_name, 3)
            current_is_sampler = True

        elif begins_with(instrument_name, "DR_"):
            instrument_name = cut_first(instrument_name, 3)
            current_is_drone = True

            assert current_group_name != "", "Must provide a :group when declaring a DR_ synth"
            assert current_default_args_string != "", "Must provide default args when declaring a DR_ synth"

        return SynthHeader(instrument_name, current_is_drone, current_is_sampler, is_selected, current_default_args_string, additional_config_string)
