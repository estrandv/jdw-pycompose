from parse_classes import EffectDefinition, SynthHeader
from shuttle_notation import ResolvedElement
from pythonosc.osc_message import OscMessage
from enum import Enum
from decimal import Decimal
from dataclasses import dataclass

class CommandContext(Enum):
    UPDATE = 0
    QUEUE = 1
    ALL = 2

@dataclass
class BillboardCommand:
    address: str
    context: CommandContext
    args: list[str]

@dataclass
class EffectMessage:
    effect: EffectDefinition
    external_id: str
    synth_name: str
    osc_args: list[str | float]

@dataclass
class PadConfig:
    pad_number: int
    configured_index: int

@dataclass
class BillboardKeyConfiguration:
    instrument_name: str
    pads_config: list[PadConfig]
    args: dict[str, Decimal]
    for_sampler: bool

# Contains the original element and the message it was resolved as
@dataclass
class ElementMessage:
    element: ResolvedElement
    osc: OscMessage

    def get_time(self) -> str:
        return str(self.element.args["time"]) if "time" in self.element.args else "0.0"


@dataclass
class BillboardTrack:
    messages: list[ElementMessage]
    group_name: str


@dataclass
class BillboardSynthSection:
    # By name
    tracks: dict[str, BillboardTrack]
    effects: list[EffectMessage]
    key_configuration: BillboardKeyConfiguration | None
    header: SynthHeader

@dataclass
class Billboard:
    sections: list[BillboardSynthSection]
    group_filters: list[list[str]]
    commands: list[BillboardCommand]

    def get_final_filter(self) -> list[str]:
        return self.group_filters[-1] if len(self.group_filters) > 0 else []
