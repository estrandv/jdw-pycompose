# Purpose: master method for parsing the entire billboard from a source string by orchestrating other libs.
# TODO: Rethink purpose and class placement

from filtering import extract_commands, extract_default_args, extract_group_filters, extract_synth_chunks
from line_classify import classify_lines
from parsing import BillboardSynthSection, process_synth_section, parse_command, BillboardCommand, parse_synth_chunk

from dataclasses import dataclass

@dataclass
class Billboard:
    sections: list[BillboardSynthSection]
    group_filters: list[list[str]]
    commands: list[BillboardCommand]

    def get_final_filter(self) -> list[str]:
        return self.group_filters[-1] if len(self.group_filters) > 0 else []

# TODO: Consider scope of this file - this is an orchestration method but other parts are more final-step
def parse_billboard(billboard_string: str) -> Billboard:
    lines = classify_lines(billboard_string)
    filters = extract_group_filters(lines)
    billboard_default_args = extract_default_args(lines)
    command_lines = extract_commands(lines)
    commands = [parse_command(line) for line in command_lines]

    synth_chunks = extract_synth_chunks(lines)

    synth_sections = [parse_synth_chunk(chunk) for chunk in synth_chunks]

    sections: list[BillboardSynthSection] = [process_synth_section(s, billboard_default_args) for s in synth_sections]

    return Billboard(sections, filters, commands)




# Tests
if __name__ == "__main__":
    example_billboard = """

#############
# T R A C K S ¶
#############

### NRT TESTING; NOT COMPO
#>>> keys
#>>> drum

### Could use a repeating structure, but heavily dependant on any eventual vocals ...

#>>> boom reed hreed keys bass cele drum hdrum

/set_bpm 120


# TODO: Some of these are too long to even send to sc - re-evaluate what is sent with an nrt record message!

>>> boom reed
>>> drum hdrum keys bass reed cymbal
>>> drum hdrum keys bass cele cymbal
>>> drum hdrum bass prophet cymbal boom hreed

>>> drum hdrum keys cymbal prophet cymbal experiment
>>> drum hdrum keys bass rails cymbal boom
#>>> drum hdrum keys bass rails cymbal boom
>>> drum hdrum keys cymbal prophet cymbal experiment

>>> drum hdrum keys bass cymbal cele cymbal
>>> drum hdrum bass cymbal reed hreed boom cymbal

>>> drum hdrum keys cymbal prophet cymbal experiment
>>> drum hdrum keys bass rails cymbal boom reed
#>>> drum hdrum keys bass rails cymbal boom reed

>>> keys reed prophet insanity cymbal
>>> drum hdrum bass keys reed hreed prophet insanity boom
#>>> end

#>>> experiment

@prophet
@blip
@ksBass
@dBass
@eBass

# NOTE: detectsilence can mess up drones that go out of arrangement - never quiet such a drone to amp 0 after starting.
# Sadly, this means ctrl+k can mess things up.
@DR_aPad:experiment amp0.0,out90

    #(a4 a4 g4 g5):amp0.2
    (g5 g6 g7 d6 d7 c7 g5 c7 c8:0,amp0.01):amp0.7,gate1,pan-0.7

    €reverb:a room0.9,mix0.35,mul0.04
    €distortion:a drive0.5
    #€delay:a

*@moogBass:prophet susT0.5,sus0.01,amp1,lfoS2,cutoff4000,pan-0.1,out50

    (x:1,fish0 c6:1 e6:1 f6:1 e6:0,susT2 x:12):0.5

    # TODO: Separate unique id ordering for fx/tracks
    €delay:a echo0.25,echt4
    €reverb:a room0.9,mix0.4,mul0.9
    €clamp:a under6200,over1780

# TODO: Separate
@FMRhodes:keys

    (c5:4 c5:4 bb4:4 a4:2 bb4:2):chorus0.4,susT1.1,amp1,time0.5,sus8,len4.0,tot0.00,pan-0.2

    <cele;out20> ((c6:1 bb6:1 a6:0.5 g6:1.5 f6:1 g6:0.5 a6:1 f6:0.5 g6:0 x:0.5 x:0.5)*3 \
        (c6:1 bb6:1 a6:0.5 g6:1.5 x:1 x:0.5 x:1 x:0.5 x:0 x:1)):sus0.45,chorus0.5,relT0.8,amp0.3,cutoff1000,len8,tot7.00,pan0.3


@pluck:insanity out20

    (c7:1 c8:0.5 bb7:0.5 c8:0.5 bb7:0.5 c8:0.5 bb7:0.5 c8:1 bb7:1 g7:1 f7:0 x:1):susT0.8,time0.5,out20,sus0.2,amp1,len8,tot7.00

    (e8:0.5 e8:1 e8:0.5 e8:0 x:2):amp1,time0.5,out20,susT0.8,sus0.2,len4.0,tot2.00

    (x:2 c6:1 g6:1 f6:1 e6:1 f6:0.5 e6:1 c6:2.5 c6:1 g6:1 f6:1 e6:1 f6:0.5 e6:1 f6:0 x:0.5 \
    ):0.5,sus0.2,out20,amp1,susT0.8,len16,tot15.50

    #c8:0.25,amp0.2,pan-0.2

    #c5:0.25,amp0.4,pan-0.3


    €reverb:a room0.8,mix0.15,mul0.75
    €clamp:a under1500,over880

#@organReed

@aPad:reed out30

    # TODO: This got messed up somewhere; you can barely hear it
    <reed> (c6:0,sus4 c5:1 e5:2 c5:1 f5:1 e5:1 . c5:2 c6:0,sus4 a4:1 c5:2 a4:1 e5:1 d5:1 c5:1 d5:0 x:1 \
        ):0.5,susT0.5,amp*1,sus0.75,len16,tot15.00,pan0.1

    <hreed> (bb6:1 c7:2 f6:2 c6:2 g6:4 bb6:1 g6:2 f6:1 e6:1 f6:1 c7:2 e6:2 f6:2 bb6:2 a6:3.5 c6:0 x:3.5 \
        ):sus2,susT1,amp*0.45,time0.5,len32,tot28.50,pan0.15


    €clamp:a under1900,over140


@eBass:bass out60

    (c4:4 c4:4 bb3:4 a3:2 bb3:2):chorus0.4,susT1.1,amp1,time0.5,sus8,len4.0,tot0.00,cutoff200,pan0.2

    €clamp:a under800,over140

@blip:rails out54
    (c6:1 c7:1 bb6:1 g6:1 a6:1 c6:3 f6:1 bb6:1 f6:1 g6:0.5 a6:0.5 g6:1 \
        f6:1 c6:2 c7:1 bb6:1 g6:1 f6:1 g6:1 c6:3 f6:1 g6:3 a6:1 g6:1 f6:0 x:2 \
        ):0.5,susT2,amp0.45,sus0.2,len32,tot30.00,pan0.05,fmod-1.4444

    (c6:1 c7:1 bb6:1 g6:1 a6:1 c6:3 f6:1 bb6:1 f6:1 g6:0.5 a6:0.5 g6:1 \
        f6:1 c6:2 c7:1 bb6:1 g6:1 f6:1 g6:1 c6:3 f6:1 g6:3 a6:1 g6:1 f6:0 x:2 \
        ):0.5,susT2,amp0.3,sus0.2,len32,tot30.00,pan0.08,out0

    # Experimental effects array, can remove everything and have a decent sounding old riff.
    €distortion:a drive0.05
    €delay:a echo0.25,echt0.05
    €reverb:a room0.3,mix0.25,mul0.08

@karp

@arpy

@prophet

@SP_youtube
    # Example of reversing - tricky with start but it seems to accept a very high number
    #1:8,rate-0.5,start9999999999999,out20,amp0.2

@SP_Roland808:drum ofs0,sus20,amp0.6,out80 1:0 2:14 3:26 4:32 5:54 6:60 7:70 8:95

    (14:1.5 14:0.5 x:1 14:1 14:1.5 14:0.5 x:2 14:1.5 14:0.5 x:1 14:1 14:1.5 14:0.5 x:0.5 14:0.5 x:1)

    €clamp:a under800,over70
    #€analogTape:a out80,out80

@SP_Roland808:hdrum ofs0,sus20,amp0.5,out40 1:0 2:14 3:26 4:32 5:54 6:60 7:70 8:95

    (x:2 95:1 x:3 95:2 x:2 95:1 x:3 95:0.5 x:0.5 95:1)
    (x:3.5 98:1.5 98:3)
    (26:1 26:2 26:1 26:0 x:0)
    <cymbal> (x:31 34:1):amp*1.4,rate0.5,out10

    # Experimental reverb... Set under5500 for pre-reverb levels
    €reverb:a room0.4,mix0.25,mul1.1
    €clamp:a under4500,over20

@SP_EMU_EDrum

@SP_EMU_SP12 ofs0,sus20,amp1,out10

    <boom> (x:31 28:1):rate0.2,amp*0.7
    <hdrum> (x:12 x:1 4:0.5 4:0.5 4*2:0.5 4:0 x:1):rate2


    €clamp:a under1200,over780

    #€analogTape:a bus0

@SP_Clavia

@SP_EMU_Proteus

@SP_Acetone

@SP_Yamaha_Grand

@SP_GBA


    """

    parse_billboard(example_billboard)
