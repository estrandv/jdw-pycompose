from dataclasses import dataclass

from pythonosc.osc_message import OscMessage
from jdw_osc_utils import create_msg
import default_synthdefs as default_synthdefs
import sample_reading as sample_reading

@dataclass
class SynthDefMessage:
    content: str
    name: str
    load_msg: OscMessage

@dataclass
class SampleMessage:
    sample: sample_reading.Sample
    load_msg: OscMessage

def get_default_synthdefs() -> list[SynthDefMessage]:

    ret: list[SynthDefMessage] = []
    for synth in default_synthdefs.get():

        name = synth.split("\"")[1]
        msg = create_msg("/create_synthdef", [synth])
        ret.append(SynthDefMessage(synth, name, msg))

    return ret

def get_default_samples() -> list[SampleMessage]:
    samples = sample_reading.read_sample_packs("~/sample_packs")
    return [SampleMessage(s, create_msg("/load_sample", s.as_args())) for s in samples]

def get_effects_clear() -> OscMessage:
    common_prefix = "effect_"
    return create_msg("/free_notes", ["^" + common_prefix + "(.*)"])
