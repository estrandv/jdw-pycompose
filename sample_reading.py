import os
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Sample:
    path: str
    sample_pack: str 
    buffer_index: int
    category: str 

    def as_args(self) -> list:
        # ("/load_sample", [wav_file, "testsamples", 100, "bd"])
        return [self.path, self.sample_pack, self.buffer_index, self.category]

def read_sample_packs(path_string: str, allowed_extensions = [".wav"]) -> list[Sample]:

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
            for file in os.listdir(pack_path):

                correct_ext = False 
                for a in allowed_extensions:
                    if a in file.lower():
                        correct_ext = True 

                if correct_ext:
                    samples.append(Sample(
                        pack_path + file,
                        pack,
                        buffer_index,
                        "" # TODO: Resolve somehow 
                    ))
                    buffer_index += 1
                    print(samples[-1])    

    return samples 
