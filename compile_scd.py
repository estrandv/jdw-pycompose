import re

# Build proper scd synthdefs from templates 
# Useful to avoid annoying scd boilerplate conventions 

# arga1.0,argb-1,argc3.000 -> arga: 1.0, argb: -1, argc: 3.000
def parse_args(arg_string: str) -> dict[str, str]:
    result = {}
    for atom in arg_string.split(","):
        letter_part = re.findall("[a-zA-z]+", atom)[0]
        result[letter_part] = atom.replace(letter_part, "")

    return result 

def find_variable(scd_call: str) -> None | str:
    if "=" in scd_call:
        return scd_call.split("=")[0].strip() 



def compile(definition: str) -> str:

    template = """
    SynthDef.new("{:name}", {|{:var_args}|
        var {:dec_args};
        {:scd_lines}
    })
    """

    # TODO: Sloppy hidden default args solution
    args = parse_args("freq440,amp1,gate1,sus1,pan0,attT0,decT0,susL1,relT0.2,out0")    

    lines = [line for line in definition.split("\n") if line != ""]
    name = lines[0].strip()
    argline = [line for line in lines if "args: " in line][0]
    rep_args = parse_args(argline.split("args: ")[1])
    for key in rep_args:
        args[key] = rep_args[key]
    scd_lines = lines[lines.index(argline)+1:]
    dec_args = [find_variable(scd_line) for scd_line in scd_lines]
    req_args = list(set([arg for arg in dec_args if arg != None and arg not in args]))

    var_args = ",".join([arg + "=" + args[arg] for arg in args])
    dec_args = ",".join(req_args)
    scd_lines_all = "\n        ".join([line.strip() for line in scd_lines])
    return template.replace("{:var_args}", var_args)\
            .replace("{:dec_args}", dec_args)\
            .replace("{:scd_lines}", scd_lines_all)\
            .replace("{:name}", name)

def get_all(path: str) -> list[str]:
    return [compile(synth) for synth in open(path, 'r').read().split("~") if synth.strip() != ""]
