from dataclasses import dataclass
from shuttle_notation import Parser, ResolvedElement

@dataclass
class BillboardEffect:
    effect_type: str
    args: dict

@dataclass
class BillboardTrack:
    synth_name: str
    is_sampler: bool
    group_name: str
    elements: list[ResolvedElement]


# Dig out configs for "sampler", "keys" and "pads" 
# Example
"""
@synth brute:arg1
@sampler Roland808:arg2
@pads 1:8 2:3 4:6 ... 
"""
def parse_keyboard_config(source: str, parser: Parser) -> dict[str,list[ResolvedElement]]:
    configs = {}
    for line in source.split("\n"):
        raw = line.split("#")[0] if "#" in line else line
        data = raw.strip()
        if data != "" and data[0] == "@":
            tag = "".join(data[1:]).split(" ")[0]
            rest = data.replace("@" + tag + " ", "")
            configs[tag] = parser.parse(rest)
    return configs

# Drones are just single-element shuttle strings, e.g. "reverb:in4,out0"
def parse_drone_billboard(billboard: str, parser: Parser) -> dict[str,BillboardEffect]:
    effects = {}
    current_instrument = ""

    for line in billboard.split("\n"):
        # Remove commented and whitespace
        raw = line.split("#")[0] if "#" in line else line
        data = raw.strip()

        if data != "":
            if data[0] == "@":
                # Define current instrument with @ 
                instrument_name = "".join(data[1:])
                current_instrument = instrument_name
            elif current_instrument != "":

                element = parser.parse(data)[0]
                effect_id = element.suffix

                print(effect_id, element.args)

                effects[effect_id] = BillboardEffect(current_instrument, element.args)

    return effects 

def parse_track_billboard(billboard: str, parser: Parser) -> dict[str,BillboardTrack]:
    
    tracks = {}

    group_filter = ""
    current_instrument = ""
    current_is_sampler = False 
    # Used to give tracks unique ids per-instrument
    instrument_count = 0

    # TODO: Can do line breaks as:
    # - if last non-white char is "\"
    # - set line-\ as "lastLine" and continue
    # - else, if lastLine is populated, consume it to form start of line

    for line in billboard.split("\n"):

        # Remove commented and whitespace
        raw = line.split("#")[0] if "#" in line else line
        data = raw.strip()

        # Establish group filter
        if ">>>" in data:
            group_filter = "".join(data.split(">>>")[1:])
            continue 

        # Up count for actual tracks, even if commented
        if "#" in line or (data != "" and data[0] != "@"):
            instrument_count += 1

        if data != "":
            if data[0] == "@":
                # Define current instrument with @ 
                instrument_name = "".join(data[1:])
                if "".join(instrument_name[0:3]) == "SP_":
                    instrument_name = "".join(instrument_name[3:])
                    current_is_sampler = True
                else: 
                    current_is_sampler = False 
                
                current_instrument = instrument_name
                instrument_count = 0
 
            elif current_instrument != "":

                # Create track 
                track_data = data
                meta_data = "" 
                group_name = ""
                if data[0] == "<" and ">" in data:
                    track_data = "".join(data.split(">")[1:])
                    # Between <...>
                    meta_data = "".join(data.split(">")[0][1:])

                    # TODO: No further meta_data atm
                    group_name = meta_data.split(",")[0]

                filter_ok = group_filter == "" or group_name == "" \
                    or (group_name in group_filter.split(" "))

                if filter_ok:

                    elements = parser.parse(track_data)

                    track_id = current_instrument + "_" + str(instrument_count)

                    print(track_id)

                    tracks[track_id] = BillboardTrack(
                        current_instrument,
                        current_is_sampler,
                        group_name,
                        elements
                    )

        
    return tracks 

### TODO: OSC stuff below, might move to its own lib 

from jdw_shuttle_lib.shuttle_jdw_translation import ElementWrapper, MessageType
import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils
from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_packet import OscPacket


def create_notes_b(elements: list[ResolvedElement], synth_name, is_sample = False) -> list[OscBundle]:
    sequence = []
    for element in elements:

        wrapper = ElementWrapper(element, synth_name, MessageType.PLAY_SAMPLE if is_sample else MessageType.NOTE_ON_TIMED)
        
        msg = jdw_osc_utils.create_jdw_note(wrapper)

        if msg != None:
            sequence.append(msg)

    return sequence

def create_sequencer_queue_bundles(tracks: dict[str,BillboardTrack]) -> list[OscBundle]:
    bundles = []
    for track_name in tracks:
        track = tracks[track_name]

        sequence = create_notes_b(track.elements, track.synth_name, track.is_sampler)
        
        bundles.append(jdw_osc_utils.create_queue_update_bundle(track_name, sequence))

    return bundles 

# Creates a batch queue bundle to queue all mentioned tracks at once
def create_sequencer_queue_bundle(tracks: dict[str,BillboardTrack], stop_missing = True) -> OscBundle:
    
    bundles = create_sequencer_queue_bundles(tracks)
    return jdw_osc_utils.create_batch_queue_bundle(bundles, stop_missing)

def create_nrt_record_bundles(tracks: dict[str,BillboardTrack], zero_time_messages: list[OscPacket] = [], bpm = 120) -> list[OscBundle]:

    bundles = []
    for track in tracks:

        # Append zero time messages before converting all sequences
        sequence = [jdw_osc_utils.to_timed_osc("0.0", msg) for msg in zero_time_messages] \
            + create_notes_b(tracks[track].elements, tracks[track].synth_name, tracks[track].is_sampler)

        # Example nrt send 
        # TODO: Hardcodes, but fine for now since it's not public-facing 
        file_name = "/home/estrandv/jdw_output/track_" + track + ".wav"
        end_time = sum([float(e.args["time"]) for e in tracks[track].elements]) + 4.0 # A little extra 
        
        bundles.append(jdw_osc_utils.create_nrt_record_bundle(sequence, file_name, end_time, bpm))

    return bundles 

def create_keyboard_config_packets(configs: dict[str,list[ResolvedElement]]) -> list[OscPacket]:
    packets = []
    
    for config_key in configs:
        config = configs[config_key]
        subtype = config[0].suffix
        # TODO: Some overhead here, with the wrapper args 
        content = [ElementWrapper(e, subtype, MessageType.NOTE_ON_TIMED) for e in config]
        if config_key == "synth":
            args = content[0].args_as_osc()
            packets.append(jdw_osc_utils.create_msg("/keyboard_instrument_name", [subtype]))
            packets.append(jdw_osc_utils.create_msg("/keyboard_args", args))
        elif config_key == "pads":
            for e in config:
                # e.g. 22:5
                pad_id = e.index
                sample_index = int(e.args["time"])

                # TODO: Currently not a real message 
                packets.append(jdw_osc_utils.create_msg("/keyboard_pad_sample", [pad_id, sample_index]))
        elif config_key == "sampler":
            args = content[0].args_as_osc()
            subtype = content[0].instrument_name
            # TODO: Currently not real messages
            packets.append(jdw_osc_utils.create_msg("/keyboard_sample_pack", [subtype]))
            packets.append(jdw_osc_utils.create_msg("/keyboard_sample_args", args))

    packets.append(jdw_osc_utils.create_msg("/keyboard_quantization", ["0.25"])) # TODO: Not yet in billboard 

    return packets 

def create_effect_recreate_packets(effects: dict[str,BillboardEffect]) -> list[OscPacket]:

    packets = []
    common_prefix = "effect_"
    packets.append(jdw_osc_utils.create_msg("/free_notes", ["^" + common_prefix + "(.*)"]))
    for effect_name in effects:
        effect = effects[effect_name]
        osc_args = []
        for arg in effect.args:
            if arg not in osc_args:
                osc_args.append(arg)
                osc_args.append(float(effect.args[arg]))

        external_id = common_prefix + effect_name

        packets.append(jdw_osc_utils.create_msg("/note_on", [effect.effect_type, external_id, 0] + osc_args))

    return packets

def create_effect_mod_packets(effects: dict[str,BillboardEffect]) -> list[OscPacket]:
    packets = []
    common_prefix = "effect_"
    for effect_name in effects:
        effect = effects[effect_name]
        osc_args = []
        for arg in effect.args:
            if arg not in osc_args:
                osc_args.append(arg)
                osc_args.append(float(effect.args[arg]))

        external_id = common_prefix + effect_name

        packets.append(jdw_osc_utils.create_msg("/note_modify", [external_id, 0] + osc_args))
    return packets

if __name__ == "__main__":
    parser = Parser() 
    parser.arg_defaults = {"time": 0.0, "sus": 0.0} # Because of to_timed_osc expectation + timed_play expectation

    effects = parse_drone_billboard("""
    @reverb
    effect_one:in4,out0

    @synth
    drone:amp0
    
    """, parser)

    tracks = parse_track_billboard("""
    
    >>> fish leaf

@SP_cake
    <leaf> g6
    <not_leaf> g8
    

    @synth
    <fish> a4 a5 a5
    # <fish> commented:0
    
    
    """, parser)

    assert tracks["synth_0"].elements[2].prefix == "a"
    assert tracks["cake_0"].elements[0].prefix == "g"
    assert tracks["synth_0"].group_name == "fish"
    assert tracks["cake_0"].is_sampler
    assert tracks["synth_0"].is_sampler == False 
    assert len(tracks) == 2

    keyboard_conf = parse_keyboard_config("""
    
    @synth 1:2 3:4
    @pads fish:arg1,arg2
    # @miss 1:0
    
    """, parser)

    assert keyboard_conf["synth"][1].index == 3
    assert keyboard_conf["pads"][0].suffix == "fish"
    assert "miss" not in keyboard_conf

    create_sequencer_queue_bundle(tracks)
    create_nrt_record_bundles(tracks, bpm=111)
    create_keyboard_config_packets(keyboard_conf)
    create_effect_mod_packets(effects)
    create_effect_recreate_packets(effects)