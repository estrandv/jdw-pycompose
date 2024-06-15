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
        if "#" in line and data != "" and data[0] != "@":
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

                        tracks[track_id] = BillboardTrack(
                            current_instrument,
                            current_is_sampler,
                            group_name,
                            elements
                        )

        
    return tracks 

if __name__ == "__main__":
    parser = Parser() 

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
    
    @moop 1:2 3:4
    @mäp fish:arg1,arg2
    # @miss 1:0
    
    """, parser)

    assert keyboard_conf["moop"][1].index == 3
    assert keyboard_conf["mäp"][0].suffix == "fish"
    assert "miss" not in keyboard_conf