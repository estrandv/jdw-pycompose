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

@dataclass
class SynthSection:
    header: SynthHeader
    tracks: list[TrackDefinition]
    effects: list[EffectDefinition]
