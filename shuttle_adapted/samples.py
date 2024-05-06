import os
from pathlib import Path
from dataclasses import dataclass
import jdw_osc_utils
from pythonosc import osc_message_builder, udp_client, osc_bundle_builder

@dataclass
class Sample:
    path: str
    sample_pack: str 
    buffer_index: int
    category: str 

    def as_args(self) -> list:
        # ("/load_sample", [wav_file, "testsamples", 100, "bd"])
        return [self.path, self.sample_pack, self.buffer_index, self.category]


def read_sample_packs() -> list[Sample]:

    home = str(Path.home())
    samples_root = home + "/sample_packs/"

    samples = []

    buffer_index = 100
    for pack in os.listdir(samples_root):
        pack_path = samples_root + pack + "/"
        if os.path.isdir(pack_path):
            for file in os.listdir(pack_path):
                if ".wav" in file:
                    samples.append(Sample(
                        pack_path + file,
                        pack,
                        buffer_index,
                        "" # TODO: Resolve somehow 
                    ))
                    buffer_index += 1
                    print(samples[-1])    


    return samples 

# TODO: make something smarter later - for now just run it directly... 
client = udp_client.SimpleUDPClient("127.0.0.1", 13339) # Router

for sample in read_sample_packs():
    client.send(jdw_osc_utils.create_msg("/load_sample", sample.as_args()))