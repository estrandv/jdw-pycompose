import os
from pathlib import Path
from dataclasses import dataclass
from natsort import natsorted # Proper sorting of strings that might contain numbers
from pythonosc.osc_message import OscMessage
from jdw_billboarding.lib.jdw_osc_utils import create_msg

from jdw_billboarding.lib.external_data_classes import SampleMessage, SynthDefMessage, Sample

# TODO: Porting of as much as possible from the earlier convenience methods in pycompose
# Move here first, then work on making it make sense ...

def read_sample_packs(path_string: str, allowed_extensions: list[str] = [".wav"]) -> list[Sample]:

    if len(path_string) == 0:
        return []

    if path_string[0] == "~":
        path_string = str(Path.home()) + "".join(path_string[1:])

    samples_root = path_string

    if samples_root[-1] != "/":
        samples_root += "/"

    samples: list[Sample] = []

    # Mainly a helper struct for indexing by category
    categorized_samples: dict[str, list[Sample]] = {}

    buffer_index = 100
    for pack in os.listdir(samples_root):
        pack_path = samples_root + pack + "/"
        if os.path.isdir(pack_path):
            raw_files = os.listdir(pack_path)

            filtered_files = []
            for file in raw_files:
                if any([ext.lower() in file.lower() for ext in allowed_extensions]):
                    filtered_files.append(file)

            files = natsorted(filtered_files)

            tone_index = 0

            for file in files:

                category = _get_category(file)

                new_tone_index = tone_index
                tone_index += 1

                samples.append(Sample(
                    pack_path + file,
                    pack,
                    buffer_index,
                    category,
                    new_tone_index
                ))

                buffer_index += 1

    return samples

def _get_category(file_name) -> str:
    matchers: dict[str, list[str]] = {
        "bd": ["bd"],
        "hh": ["hh", "hat", "ride"],
        "cy": ["cy", "crash", "cr"],
        "sn": ["sn", "sd"],
        "be": ["cb", "bell"],
        "to": ["lt", "ht", "tom", "mc", "lb", "to"],
        "sh": ["mc", "ma", "sh"],
        "fx": ["fx"],
        "st": ["st"]
    }

    for category in matchers:
        for keyword in matchers[category]:
            if keyword in file_name.lower():
                return category

    return ""


def _defsynthdef_get() -> list[str]:

    defs: list[str] = []
    # TODO: Not sure how to get "path of script but not path of any script executing the script"
    with open("/home/estrandv/programming/jdw-pycompose/scd/synthDefs.scd") as synthDefs:
        content = synthDefs.read()
        for cut in content.split("SynthDef.new"):
            if cut.strip() != "":
                full = "SynthDef.new" + cut
                defs.append(full)

    import compile_scd
    for s in compile_scd.get_all("/home/estrandv/programming/jdw-pycompose/scd-templating/template_synths.txt"):
        defs.append(s)

    return defs

def get_default_synthdefs() -> list[SynthDefMessage]:

    ret: list[SynthDefMessage] = []
    for synth in _defsynthdef_get():

        name = synth.split("\"")[1]
        msg = create_msg("/create_synthdef", [synth])
        ret.append(SynthDefMessage(synth, name, msg))

    return ret

def get_default_samples() -> list[SampleMessage]:
    samples = read_sample_packs("~/sample_packs")
    return [SampleMessage(s, create_msg("/load_sample", s.as_args())) for s in samples]
