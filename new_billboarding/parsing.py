from shuttle_notation.parsing.element import ResolvedElement
from shuttle_notation.parsing.full_parse import Parser
from shuttle_notation.parsing.information_parsing import DynamicArg, parse_args
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
    is_drone: bool
    is_sampler: bool
    is_selected: bool
    default_args_string: str
    additional_args_string: str
    group_name: str

def cut_first(source: str, amount: int) -> str:
    possible = len(source) >= amount
    return "".join(source[amount:]) if possible else ""

def parse_effect_definition(content: str):

    space_split = content.split(" ")
    # Cut off the "€ or ¤"
    core_part = cut_first(space_split[0], 1)

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

        return SynthHeader(instrument_name, current_is_drone, current_is_sampler, is_selected, current_default_args_string, additional_config_string, current_group_name)


class CommandContext(Enum):
    UPDATE = 0
    QUEUE = 1
    ALL = 2

@dataclass
class BillboardCommand:
    address: str
    context: CommandContext
    args: list[str]

# TODO: Move to parsing, along with classes
def parse_command(line: str) -> BillboardCommand:
    split = line.strip().split(" ")
    type_notation: str = split[0]

    context: CommandContext = CommandContext.ALL
    if type_notation == QUEUE_COMMAND_SYMBOL:
        context = CommandContext.QUEUE
    elif type_notation == UPDATE_COMMAND_SYMBOL:
        context = CommandContext.UPDATE

    args: list[str] = split[2:] if len(split) > 2 else []
    return BillboardCommand(split[1], context, args)


# Parse the shuttle string of the track, resolving any arg inheritance, returning the list of its elements
def parse_track(track: TrackDefinition, default_arg_string: str) -> list[ResolvedElement]:
    # Easiest way to apply default args
    full_source = "(" + track.content + "):" + default_arg_string if default_arg_string != "" else track.content
    override_args = parse_args(track.arg_override, {})
    elements = Parser().parse(full_source)

    _arg_override(elements, override_args)

    return elements

# Applies args after the fact, mutating the elements
# Supports args with operators
def _arg_override(elements: list[ResolvedElement], override: dict[str,DynamicArg]):
    for arg_key in override:
        override_arg = override[arg_key]
        for element in elements:
            new_value = override_arg.value
            if arg_key in element.args:
                if override_arg.operator == "*":
                    element.args[arg_key] *= new_value
                elif override_arg.operator == "+":
                    element.args[arg_key] += new_value
                elif override_arg.operator == "-":
                    element.args[arg_key] -= new_value
                else:
                    element.args[arg_key] = new_value
            else:
                element.args[arg_key] = new_value

# Tests
if __name__ == "__main__":

    assert cut_first("abcd", 3) == "d"
    assert cut_first("    ", 1) == "   "
    assert cut_first("a", 0) == "a"
    assert cut_first("a", 1) == ""
    assert cut_first("0", 2) == ""

    # Quick unasserted execution happy-case
    parse_synth_header("@SP_mysynth:group arg1,arg2,arg3 1:1 2:2 3:3")
    parse_track_definition("c4 g4 f2 x", 0)
    parse_effect_definition("€effect:req arg1,arg2,arg3")
    parse_track(TrackDefinition("c4 c4 d4", "special", "sus4.0", 1), SynthHeader("synth", False, False, False, "arg2.0", "22:2", "group"))
