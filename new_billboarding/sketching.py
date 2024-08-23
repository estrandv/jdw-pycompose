from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_message import OscMessage
from shuttle_notation.parsing.element import ResolvedElement
from shuttle_notation.parsing.full_parse import Parser
from shuttle_notation.parsing.information_parsing import parse_args
from jdw_shuttle_lib.jdw_osc_utils import create_msg, to_timed_osc
from jdw_shuttle_lib.shuttle_jdw_translation import args_as_osc, is_symbol, to_note_mod, to_note_on, to_note_on_timed, to_play_sample
from new_billboarding import raw_billboard
from new_billboarding.filtering import extract_group_filters, extract_synth_chunks
from new_billboarding.line_classify import begins_with, classify_lines
from new_billboarding.parsing import EffectDefinition, SynthHeader, TrackDefinition, cut_first
from raw_billboard import SynthSection, create

from dataclasses import dataclass

# Contains the original effect and the message it was resolved as
@dataclass
class EffectMessage:
    effect: EffectDefinition
    external_id: str
    synth_name: str
    osc_args: list[str | float]

    def as_create_osc(self) -> OscMessage:
        return create_msg("/note_on", [self.synth_name, self.external_id, 0] + self.osc_args)

    def as_mod_osc(self) -> OscMessage:
        return create_msg("/note_modify", [self.external_id, 0] + self.osc_args)

# Contains the original element and the message it was resolved as
@dataclass
class ElementMessage:
    element: ResolvedElement
    osc: OscMessage

    def get_time(self) -> str:
        return str(self.element.args["time"]) if "time" in self.element.args else "0.0"

def parse_track(track: TrackDefinition, header: SynthHeader) -> list[ElementMessage]:

    # Easiest way to apply default args
    full_source = "(" + track.content + "):" + header.default_args_string if header.default_args_string != "" else track.content

    override_args = parse_args(track.arg_override, {})
    elements = Parser().parse(full_source)
    _arg_override(elements, override_args)

    messages: list[ElementMessage] = []
    for element in elements:

        ### Taken from the original type fetcher, to be expanded with broader context (sample, drone, etc)

        if begins_with(element.suffix, "@"):
            # Remove symbol from suffix to create note mod external id
            messages.append(ElementMessage(element, to_note_mod(element, cut_first(element.suffix, 1))))
            pass
        elif is_symbol(element, "x"):
            messages.append(ElementMessage(element, create_msg("/empty_msg", [])))
            # Silence
            pass
        elif is_symbol(element, "."):
            # Ignore
            pass
        elif is_symbol(element, "§"):
            # Loop start marker
            messages.append(ElementMessage(element, create_msg("/loop_started", [])))
            pass
        elif begins_with(element.suffix, "$"):
            # Drone, note that suffix is trimmed similar to for note mod
            messages.append(ElementMessage(element, to_note_on(element, header.instrument_name, cut_first(element.suffix, 1))))
            pass
        else:
            # Default (sample / note timed)

            # Drone tracks use note mod by default
            if header.is_drone:
                messages.append(ElementMessage(element, to_note_mod(element)))
            elif header.is_sampler:
                messages.append(ElementMessage(element, to_play_sample(element, header.instrument_name)))
            else:
                messages.append(ElementMessage(element, to_note_on_timed(element, header.instrument_name)))


    return messages

def parse_effects(effects: list[EffectDefinition], header: SynthHeader) -> list[EffectMessage]:
    msgs: list[EffectMessage] = []
    for effect in effects:
        # TODO: Not sure about blank scenarios here
        arg_source = ",".join([header.default_args_string, effect.args_string])
        args = parse_args(arg_source)
        osc_args = args_as_osc(args, [])
        external_id = "effect_" + effect.unique_suffix + "_" + header.group_name
        msgs.append(EffectMessage(effect, external_id, header.instrument_name, osc_args))

    return msgs

def full(billboard_string: str):
    lines = classify_lines(billboard_string)
    filters = extract_group_filters(lines)
    synth_chunks = extract_synth_chunks(lines)
    raw_billboard = create(filters, synth_chunks)

    for synth_section in raw_billboard.synth_sections:

        # Combine args for the tracks to create the actual arg strings
        # Parse tracks with added ():-args
        # Parse other args
        # Parse pads config
        # Perform osc message conversion

        # NOTE: The structs we have now are probably the final ones; any additional parsing
        # can be done in helper methods here

        # TODO: Working on better conversion methods in shuttle_jdw_translation
        # Gonna make some corner case conversion inline here instead

        ###

        # Track conversion
        for track in synth_section.tracks:
            resolved = parse_track(track, synth_section.header)

        ####




        pass


@dataclass
class PadConfig:
    pad_number: int
    configured_index: int

def parse_pads_config(source_string: str, parser: Parser) -> list[PadConfig]:
    elements = parser.parse(source_string)

    # e.g. 22:5
    # TODO: Then convert to /keyboard_pad_samples k v k v ...
    return [PadConfig(e.index, int(e.args["time"])) for e in elements]

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
