from dataclasses import dataclass
from shuttle_notation import Parser, ResolvedElement
from shuttle_notation.parsing.information_parsing import parse_args
from shuttle_notation.parsing.information_parsing import DynamicArg

@dataclass
class BillboardEffect:
    effect_type: str
    args: dict

@dataclass
class BillBoardPrompt:
    address: str
    args: list[str] # e.g. /address arg arg arg arg 

@dataclass
class BillboardTrack:
    synth_name: str
    is_sampler: bool
    is_drone: bool 
    group_name: str
    elements: list[ResolvedElement]
    is_selected: bool 
    pads_config: list[ResolvedElement]
    default_arg_string: str

@dataclass
class BillBoard:
    tracks: dict[str, BillboardTrack]
    effects: dict[str, BillboardEffect]
    drones: dict[str, BillboardEffect]
    prompts: list[BillBoardPrompt]
    group_filters: list[list[str]]

# Applies args after the fact, mutating the elements
# Supports args with operators
def arg_override(elements: list[ResolvedElement], override: dict[str,DynamicArg]):
    for arg_key in override:
        override_arg = override[arg_key]
        for element in elements:
            new_value = override_arg.value
            if arg_key in element.args:
                if override_arg.operator == "*":
                    element.args[arg_key] *= new_value
                elif override_arg.operator == "+":
                    element.args[arg_key] += new_value
                elif override_arg.operator == "-":
                    element.args[arg_key] -= new_value
                else:
                    element.args[arg_key] = new_value
            else:
                element.args[arg_key] = new_value


# Split by newline, treating backslash as line continuation
def line_split(source: str) -> list[str]:
    return [line.strip().replace("\t", " ").replace("    ", " ") for line in source.split("\n")]

# Drones are just single-element shuttle strings, e.g. "reverb:in4,out0"
def parse_drone_billboard(billboard: str, parser: Parser) -> dict[str,BillboardEffect]:

    result = {}
    for line in line_split(billboard):
        raw = line.split("#")[0] if "#" in line else line
        data = raw.strip()
        if data != "" and data[0] == "@":
            # Tag is the text immediately after @
            synth_name = "".join(data[1:]).split(" ")[0]
            # The rest is parsed as a shuttle string
            rest = data.replace("@" + synth_name + " ", "")
            element = parser.parse(rest)[0]
            result[element.suffix] = BillboardEffect(synth_name, element.args)

    return result

# Legacy compat after filtering changes - performs group filtering of tracks 
def parse_track_billboard(billboard: str, parser: Parser) -> BillBoard:
    billboard = parse_track_billboard_unfiltered(billboard, parser)

    group_filter = billboard.group_filters[-1] if len(billboard.group_filters) > 0 else []

    new_tracks = {}
    for track_name in billboard.tracks:
        track = billboard.tracks[track_name]

        filter_ok = len(group_filter) == 0 or track.group_name == "" \
                        or (track.group_name in group_filter)

        if filter_ok:
            new_tracks[track_name] = track

    billboard.tracks = new_tracks

    return billboard

# TODO: Should parse each sub-element separately to be less messy (effects, drones, tracks, etc.)
# TODO: Make selection its own separate kind of data 
def parse_track_billboard_unfiltered(billboard: str, parser: Parser) -> BillBoard:
    
    tracks = {}
    effects = {}
    drones = {}
    prompts = []

    group_filters: list[list[str]] = []

    current_instrument = ""
    current_is_sampler = False 
    current_is_drone = False 
    current_is_selected = False
    current_group_name = ""
    current_pads_config_string = ""
    current_default_args_string = ""
    # Used to give tracks unique ids per-instrument
    instrument_line_count = 0

    # Make a default arg string that can be added to the start of other arg strings for 
    #   easy defaulting 
    # TODO: I've completely dropped the ball on aliases - it's time to retire the parser
    base_args = []
    for key in parser.arg_defaults:
        base_args.append(key + str(parser.arg_defaults[key]))
    base_arg_string = ",".join(base_args)

    for line in line_split(billboard):

        # Remove commented and whitespace
        raw = line.split("#")[0] if "#" in line else line
        data = raw.strip()

        # Establish group filter
        if ">>>" in data:
            group_filter = "".join(data.split(">>>")[1:])
            split_filter = group_filter.split(" ")
            group_filters.append(split_filter)
            print("ADDING FILTER", split_filter)
            continue 

        # Up count for actual sequence data, even if commented
        if "#" in line or (data != "" and data[0] not in "*@€/"):
            instrument_line_count += 1

        if data != "":

            # Note selection marker on headers and remove it
            if data[0] == "*" and "@" in data:
                print("SELECTING")
                current_is_selected = True
                data = "".join(data[1:])

            # Process track headers 
            if data[0] == "@":

                # Expect format: @synth_name:group_name args (pads)
                space_split = data.split(" ")
                # Cut off the "@"
                id_string = "".join(space_split[0][1:])
                instrument_name = id_string.split(":")[0] if ":" in id_string else id_string
                current_group_name = id_string.split(":")[1] if ":" in id_string else ""

                current_default_args_string = space_split[1] if len(space_split) > 1 else ""

                if "".join(instrument_name[0:3]) == "SP_":
                    instrument_name = "".join(instrument_name[3:])
                    current_is_sampler = True

                    # Include pads configuration if provided
                    if len(space_split) > 2:
                        current_pads_config_string = space_split[2]

                else: 
                    current_is_sampler = False

                # TODO: a little bit clumsy, but should work 
                if "".join(instrument_name[0:3]) == "DR_":
                    instrument_name = "".join(instrument_name[3:])
                    current_is_drone = True 

                    assert current_group_name != "", "Must provide a :group when declaring a DR_ synth"

                    # Automatically include a drone effect when DR is declared
                    effect_args = parse_args(current_default_args_string)
                    abs_args = {}
                    for key in effect_args:
                        abs_args[key] = effect_args[key].value

                    drones[current_group_name] = BillboardEffect(instrument_name, abs_args)

                else: 
                    current_is_drone = False 

                current_instrument = instrument_name
                instrument_line_count = 0

            # Process effect/drone messages 
            elif data[0] in "€":
                space_split = data.split(" ")
                # Cut off the "€ or ¤"
                core_part = "".join(space_split[0][1:])

                assert ":" in core_part, "Must provide a unique id for effect, e.g. " + core_part + ":myId"

                effect_type = core_part.split(":")[0]
                unique_suffix = core_part.split(":")[1]

                # Note that placing args first is an easy way to make them default
                arg_string = current_default_args_string + "," + space_split[1] \
                    if len(space_split) > 1 else current_default_args_string

                effect_args = parse_args(arg_string)
                abs_args = {}
                for key in effect_args:
                    abs_args[key] = effect_args[key].value

                # e.g. reverb_mygroup_3
                # or reverb_mygroup_a if effect was listed as reverb:a 
                external_id = effect_type + "_" + current_group_name + "_" + unique_suffix
                effects[external_id] = BillboardEffect(effect_type, abs_args)

            # Process prompts 
            elif data[0] == "/":
                space_split = data.split(" ")
                prompt_args = space_split[1:] if len(space_split
                ) > 1 else []
                prompts.append(BillBoardPrompt(space_split[0], prompt_args))

            # Process individual tracks/shuttle strings
            elif current_instrument != "":

                # Create track 
                track_data = data
                meta_data = "" 
                group_name = ""
                default_args = {}
                if data[0] == "<" and ">" in data:
                    assert not ("€" in data), "€ can not be used in tandem with <>-overriding"
                    track_data = "".join(data.split(">")[1:])
                    # Between <...>
                    meta_data = "".join(data.split(">")[0][1:])

                    # Handle meta_data as <group_name;args>
                    meta_split = meta_data.split(";")
                    group_name = meta_split[0]
                    default_args = parse_args(meta_split[1]) if len(meta_split) > 1 else default_args


                final_group = group_name if group_name != "" else current_group_name

                # Append a top section for default args and then parse
                parse_string = track_data
                if current_default_args_string != "":
                    parse_string = "(" + parse_string + "):" + current_default_args_string
                elements = parser.parse(parse_string)

                arg_override(elements, default_args)

                spacer = "_" + final_group + "_" if final_group != "" else "_"

                track_id = current_instrument + spacer + str(instrument_line_count)

                final_arg_strings = [string for string in [base_arg_string, current_default_args_string] if string != ""]
                final_arg_string = ",".join(final_arg_strings) if final_arg_strings else ""

                tracks[track_id] = BillboardTrack(
                    current_instrument,
                    current_is_sampler,
                    current_is_drone,
                    final_group,
                    elements,
                    current_is_selected,
                    parser.parse(current_pads_config_string),
                    current_default_args_string
                )

                # A bit of a hack, but once we have noted at least one track as selected for the instrument 
                # we have what we need and can reset 
                current_is_selected = False

    return BillBoard(tracks, effects, drones, prompts, group_filters)    
    
### TODO: OSC stuff below, might move to its own lib 

from jdw_shuttle_lib.shuttle_jdw_translation import ElementWrapper, MessageType
import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils
from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_packet import OscPacket


def create_notes_b(elements: list[ResolvedElement], synth_name, is_sample = False) -> list[OscBundle]:
    sequence = []
    for element in elements:

        wrapper = ElementWrapper(element, synth_name, MessageType.PLAY_SAMPLE if is_sample else MessageType.NOTE_ON_TIMED)
        
        msg = jdw_osc_utils.create_sequencer_note(wrapper)

        if msg != None:
            sequence.append(msg)

    return sequence

def _track_to_sequence(track: BillboardTrack) -> list[OscBundle]:
    # Unique handling for drones that hack-skips normal shuttle-based type resolution 
    # Lots of duplicate code here, TODO: fix later 
    sequence = []
    if track.is_drone:
        sequence = []
        for element in track.elements:
            # TODO: This does nothing - I just want default args support without littering 
            wrp = ElementWrapper(element, "N/A", MessageType.DRONE)
            freq = wrp.resolve_freq()
            element.args["freq"] = freq
            print(element.args) 
            osc_args = wrp.args_as_osc([])
            ext_id = drone_prefix + track.group_name
            msg = jdw_osc_utils.create_msg("/note_modify", [ext_id, jdw_osc_utils.SC_DELAY_MS] + osc_args)
            if msg != None: 
                print("Implicitly created a drone modify note for id: ", ext_id)
                sequence.append(jdw_osc_utils.to_timed_osc(str(element.args["time"]), msg))
    else:
        sequence = create_notes_b(track.elements, track.synth_name, track.is_sampler)

    return sequence

# TODO: Complete mess atm due to experimental drone parsing
# I suspect we might have to break the billboard parse into several parse methods, each focusing on something specialized 
def create_sequencer_queue_bundles(tracks: dict[str,BillboardTrack], drone_prefix = "effect_") -> list[OscBundle]:
    bundles = []
    for track_name in tracks:
        track = tracks[track_name]

        sequence = _track_to_sequence(track)

        bundles.append(jdw_osc_utils.create_queue_update_bundle(track_name, sequence))

    return bundles 

# Creates a batch queue bundle to queue all mentioned tracks at once
def create_sequencer_queue_bundle(tracks: dict[str,BillboardTrack], stop_missing = True) -> OscBundle:
    
    bundles = create_sequencer_queue_bundles(tracks)
    return jdw_osc_utils.create_batch_queue_bundle(bundles, stop_missing)

# TODO: Extremely out of date, does not account for drones, probably not effects either 
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

# Configure keyboard to use selected tracks from the billboard and their args and pad specs
def create_keys_config_packets(billboard: BillBoard) -> list[OscPacket]:
    
    packets = []

    all_selected = [key for key in billboard.tracks if billboard.tracks[key].is_selected]
    samplers = [key for key in all_selected if billboard.tracks[key].is_sampler]
    synths = [key for key in all_selected if not billboard.tracks[key].is_sampler]
    
    if len(samplers) > 0:
        selected_sampler = billboard.tracks[samplers[-1]]
        
        # Arg bit is a little hacky, since it is already applied to the elements and 
        #   only kept as a string for this specific purpose
        raw_args = parse_args(selected_sampler.default_arg_string)
        osc_args = []
        for arg in raw_args:
            if arg not in osc_args:
                osc_args.append(arg)
                osc_args.append(float(raw_args[arg].value))

        packets.append(jdw_osc_utils.create_msg("/keyboard_pad_pack", [selected_sampler.synth_name]))
        packets.append(jdw_osc_utils.create_msg("/keyboard_pad_args", osc_args))

        pad_args = []
        for e in selected_sampler.pads_config:

            # e.g. 22:5
            pad_id = e.index
            sample_index = int(e.args["time"])
            pad_args += [pad_id, sample_index]

        if len(pad_args) > 0:
            packets.append(jdw_osc_utils.create_msg("/keyboard_pad_samples", pad_args))


    if len(synths) > 0:

        selected_synth = billboard.tracks[synths[-1]]
        print("DEBUG: Synth selected", selected_synth)
        

        # Arg bit is a little hacky, since it is already applied to the elements and 
        #   only kept as a string for this specific purpose
        raw_args = parse_args(selected_synth.default_arg_string)
        osc_args = []
        for arg in raw_args:
            if arg not in osc_args:
                osc_args.append(arg)
                osc_args.append(float(raw_args[arg].value))

        packets.append(jdw_osc_utils.create_msg("/keyboard_instrument_name", [selected_synth.synth_name]))
        packets.append(jdw_osc_utils.create_msg("/keyboard_args", osc_args))

    return packets 

# TODO: See other todos on prefix; this is not moddable for drones atm and will reuslt in weird behaviour if changed 
def create_effect_recreate_packets(effects: dict[str,BillboardEffect], common_prefix = "effect_" ) -> list[OscPacket]:

    packets = []
    for effect_name in effects:
        effect = effects[effect_name]
        osc_args = []
        for arg in effect.args:
            if arg not in osc_args:
                osc_args.append(arg)
                osc_args.append(float(effect.args[arg]))

        external_id = common_prefix + effect_name

        print("CREATED NOTE ON", effect_name)
        packets.append(jdw_osc_utils.create_msg("/note_on", [effect.effect_type, external_id, 0] + osc_args))

    return packets

def create_effect_mod_packets(effects: dict[str,BillboardEffect], common_prefix = "effect_") -> list[OscPacket]:
    packets = []
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
    @reverb effect_one:in4,out0
    @synth drone:amp0
    
    """, parser)

    tracks = parse_track_billboard("""
    
    >>> fish leaf

*@SP_cake arg0 22:4 23:5
    <leaf> g6
    <not_leaf> g8
    

    *@synth
    <fish> a4 a5 a5
    # <fish> commented:0
    
    
    """, parser)


    assert tracks.tracks["synth_fish_1"].elements[2].prefix == "a"
    assert tracks.tracks["cake_leaf_1"].elements[0].prefix == "g"
    assert tracks.tracks["synth_fish_1"].group_name == "fish"
    assert tracks.tracks["cake_leaf_1"].is_sampler
    assert tracks.tracks["synth_fish_1"].is_sampler == False 
    assert len(tracks.tracks) == 2

    keys_config = create_keys_config_packets(tracks)
    assert len(keys_config) == 5, len(keys_config)

    meta_test = parse_track_billboard("""
    
    @noise
    <mup;bus14,cheese0,sus+1> g4:sus14 g4 g4 g4
    
    """, parser)

    print([key for key in meta_test.tracks])


    assert meta_test.tracks["noise_mup_1"].elements[0].args["bus"] == 14.0, meta_test["noise_mup_1"].elements[0].args["bus"]
    assert meta_test.tracks["noise_mup_1"].elements[0].args["cheese"] == 0.0, meta_test["noise_mup_1"].elements[0].args["cheese"]
    assert meta_test.tracks["noise_mup_1"].elements[0].args["sus"] == 15.0, meta_test["noise_mup_1"].elements[0].args["sus"]

    create_sequencer_queue_bundle(tracks.tracks)
    create_nrt_record_bundles(tracks.tracks, bpm=111)
    create_effect_mod_packets(effects)
    create_effect_recreate_packets(effects)


    linetest = line_split("""
    this is a regular line
    this is a line that should continue \
    and there is nothing you can do about it
    this is again a regular line
    
    """)

    lineresult = [line for line in linetest if line != ""]
    assert 3 == len(lineresult), lineresult