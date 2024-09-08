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
    tone_index: int

    def as_args(self) -> list[str | float | int]:
        # ("/load_sample", [wav_file, "testsamples", 100, "bd"])
        return [self.path, self.sample_pack, self.buffer_index, self.category, self.tone_index]

def read_sample_packs(path_string: str, allowed_extensions: list[str] = [".wav"]) -> list[Sample]:

    if len(path_string) == 0:
        return

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

                # TODO: No autocat support today, but leaving it somewhat readied for later support
                category = ""

                # uncategorized index is just the order index of the file by name
                # categorized indices are by-category and start from 0 again
                new_tone_index = tone_index
                if category != "":
                    if category not in categorized_samples:
                        categorized_samples[category] = []
                    new_tone_index = len(categorized_samples[category])
                else:
                    tone_index += 1

                samples.append(Sample(
                    pack_path + file,
                    pack,
                    buffer_index,
                    category,
                    new_tone_index
                ))

                buffer_index += 1

                if category != "":
                    categorized_samples[category].append(samples[-1])

    return samples
