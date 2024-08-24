import os
from pathlib import Path
from dataclasses import dataclass
from natsort import natsorted # Proper sorting of strings that might contain numbers


# read all wav files in subfolders of the given path and call for them to be registered in jdw-sc
# uses natural name sorting to ensure that samples always end up in the same order/buffers


@dataclass
class Sample:
    path: str
    sample_pack: str
    buffer_index: int
    category: str

    def as_args(self) -> list[str | float | int]:
        # ("/load_sample", [wav_file, "testsamples", 100, "bd"])
        return [self.path, self.sample_pack, self.buffer_index, self.category]

def read_sample_packs(path_string: str, allowed_extensions: list[str] = [".wav"]) -> list[Sample]:

    if len(path_string) == 0:
        return

    if path_string[0] == "~":
        path_string = str(Path.home()) + "".join(path_string[1:])

    samples_root = path_string

    if samples_root[-1] != "/":
        samples_root += "/"

    samples = []

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

            for file in files:
                samples.append(Sample(
                    pack_path + file,
                    pack,
                    buffer_index,
                    "" # TODO: Resolve somehow
                ))
                buffer_index += 1

    return samples
