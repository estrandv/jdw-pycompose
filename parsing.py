import re #Bracket scanning
import json
from sheet_note import SheetNote

symbols = {
    "=":"time",
    ">":"sus",
    "#": "amp"
}

# "amp0.1 sus0.5" -> {"amp": 0.1, "sus": 0.5}
def parse_args(string: str) -> dict[str, float]:

    # Remove whitespace
    string = string.replace(" ", "")

    parsed_values: dict[str, float] = {}

    current_symbol = ""

    parsing_number = ""

    def is_num(char: str) -> bool:
        return char.isdigit() or char == "-" or char == "."

    def parse_number(num: str) -> float:

        negate = "-" in num
        num = num.replace("-", "")

        base = float(num)

        dimension = -1.0 if negate else 1.0

        return base * dimension if base != 0.0 else base

    for i in range( len(string) ):

        char = string[i]
        if is_num(char):

            if current_symbol == "":
                print("Orphaned digit! Aborting parse...")
                break

            if current_symbol in symbols:
                current_symbol = symbols[current_symbol]
            
            parsing_number += string[i]

        else:
            if parsing_number != "":
                if current_symbol == "tone":
                    parsed_values[current_symbol] = float(parsing_number)
                else:
                    parsed_values[current_symbol] = parse_number(parsing_number)
                current_symbol = ""
                parsing_number = ""

            current_symbol += char


    if parsing_number != "":
        parsed_values[current_symbol] = parse_number(parsing_number)
        current_symbol = ""
        parsing_number = ""
   
    #print(parsed_values)
    return parsed_values

# "0 (hello) 0 0" -> list["(hello)"]
def extract_bracketed(string: str, bracket_open: str, bracket_close: str) -> list[str]:
    regex = r"{}(.*?){}".format("\\" + bracket_open, "\\" + bracket_close)
    return re.findall(regex, string)

# "1 0 5[>1.2] 4" -> ["1", "0", "5[>1.2]", "4"]
def _split_notes(sheet: str) -> list[str]:
    # Count non-bracketed spaces as "note splits"
    # Basically: "0 0[=.5 >.4]" -> "0<DIVIDE>0[=.5 >.4]"
    # Prone to silliness if you don't close your brackets.
    # Just close your damn brackets. 
    note_list = []
    
    space_scan = ""
    bracket_open = False
    for letter in compile_sheet(sheet):
        # Space separates notes unless a square-bracket section is ongoing
        if letter == " " and not bracket_open:
            note_list.append(space_scan)
            space_scan = ""
        else:
            if letter == "[" and not bracket_open:
                bracket_open = True
            elif letter == "]":
                bracket_open = False
            space_scan += letter

    # Final unclosed bit (since there is no final space)
    note_list.append(space_scan)

    return note_list

# "0lo hi0 0[=0.5] 0t" -> SheetNote list
def parse_sheet(sheet: str) -> list['SheetNote']:

    notes: list['SheetNote'] = []

    # _ marks a break (silent)
    break_parsed = sheet.replace("_", "0[#0]")

    # Example chunks: "0", "2[=0.5]", "(0/2/1/0[=0.5])"
    for chunk in _split_notes(break_parsed):
        if any(char.isdigit() for char in chunk):

            prefix = "" # E.g. "bla"
            digit_string = "" # E.g. "1.2"
            bracket_part = "" # E.g. "[bla]"
            suffix_part = "" # E.g. "bla"

            phases = ["prefix", "digit", "brackets", "suffix"]
            p = 0
            for char in chunk:

                if phases[p] == "prefix":
                    # All letters before digits are added to prefix
                    if not char.isdigit():
                       prefix += char 
                    # Once the fist digit is discovered, the prefix phase ends
                    else:     
                        p += 1
                if phases[p] == "digit":
                    if char.isdigit():
                        digit_string += char
                    else:
                        # Once a non-digit is discovered, the digit phase ends
                        if digit_string != "":
                            p += 1
                        else:
                            print("ERROR: Missing digit string")
                if phases[p] == "brackets":
                    if char == "[" or char == "]":
                        bracket_part += char
                    else:
                        if bracket_part != "" and "]" not in bracket_part:
                            bracket_part += char
                        else:
                            # If regular char follows without an opened bracket, the phase ends with blank
                            p += 1
                if phases[p] == "suffix": # TODO: Still on the same char, not workable
                    # Everything in final phase added to suffix
                    suffix_part += char
            
            # Parse the bracketed section if exists
            master_args = {}
            rel_args = {}
            mul_args = {}
            if bracket_part != "":
                de_bracketed = "".join("".join(bracket_part.split("[")[1:]).split("]")[:-1])
                # [amp0.2 sus-0.2|lfoD0.5|amp0.9]
                # | denotes a section, each section in order is [master|relative|multiplier]
                sections = de_bracketed.split("|")
                assert len(sections) < 4, "Too many sections splits in bracketed area " + de_bracketed
                types = ["master", "relative", "multiplier"]
                type_iter = 0
                for section in sections:
                    args = parse_args(section)
                    if types[type_iter] == "master":
                        master_args = args
                    if types[type_iter] == "relative":
                        for arg in args:
                            rel_args[arg] = [args[arg]]
                    if types[type_iter] == "multiplier":
                        mul_args = args
                    type_iter += 1

                master_args = parse_args(de_bracketed)

            base_args = {"amp": 1.0, "sus": 1.0, "time": 1.0} # Ensure non-null defaults
            notes.append(SheetNote(prefix, suffix_part, float(digit_string), master_args, base_args, rel_args, mul_args))

    return notes

# "0 (0/1/2) (3/4) 0" -> "0 0 3 0 0 1 4 0 0 2 3 0"
def compile_sheet(string: str) -> str:
    bracketed_parts = extract_bracketed(string, "(", ")")

    if bracketed_parts:
        contents_map = {}
        for part in bracketed_parts:
            contents_map[part] = part.split("/")
        longest = max([len(contents_map[part]) for part in contents_map])

        expanded_parts = [string] * longest
        compiled_parts = []
        part_index = 0
        for part in expanded_parts:
            wip = part 
            for tag in contents_map:
                # Circular index fetch 
                wip = wip.replace(tag, contents_map[tag][part_index % len(contents_map[tag])])
            compiled_parts.append(wip)
            part_index += 1

        return " ".join(compiled_parts).replace("(", "").replace(")", "")
    
    return string



if __name__ == "__main__":
    #print(parse_args("arg-333 bot0087 >15 amp08"))
    
    def sus_assert(string: str, expected_sus: float):
        result = parse_args(string)
        assert expected_sus == result["sus"], "Bad sus: " + str(result["sus"])

    sus_assert(">0.15", 0.15)
    sus_assert(">1.5", 1.5)
    sus_assert(">1.0", 1.0)
    sus_assert(">0.111", 0.111)
    sus_assert(">1", 1.0)
    sus_assert(">0", 0.0)
    sus_assert(">.2", 0.2)

    ###### 

    compiled = compile_sheet("0 0 (0/2/4) 0")
    assert compiled == "0 0 0 0 0 0 2 0 0 0 4 0", "Unexpected compile result " + compiled

    compiled = compile_sheet("(0 1 2 3)[att0.5]")
    print(compiled)


    notes = parse_sheet("hi22fish a2[tank2 no4] 6lip")
    
    #for note in notes:
        #print(json.dumps(note.__dict__))

    assert 3 == len(notes)
    assert "hi" == notes[0].prefix
    assert "fish" == notes[0].suffix
    assert 22.0 == notes[0].tone_value
    
    assert 2.0 == notes[1].master_args["tank"]
    assert 6.0 == notes[2].tone_value

    assert "lip" == notes[2].suffix

    notes2 = parse_sheet("0tag 0 0[=2]tagz 0")
    assert "tag" == notes2[0].suffix, notes[0].suffix
    assert "tagz" == notes2[2].suffix, notes[1].suffix

    notes3 = parse_sheet("_ _ 4 _")
    #print([note.__dict__ for note in notes3])

    ### Complex args
    def test_complex(sheet, arg, value):
        notes4 = parse_sheet(sheet)
        assert value == notes4[0].get_args()[arg], "Failure in sheet " + sheet + ", Actual value: " + str(notes4[0].get_args()[arg])
    
    test_complex("0[amp0.1|amp1.0|amp1.0]", "amp", 1.1)
    test_complex("4[||amp0.5]", "amp", 0.5)
    test_complex("8[|amp-0.7]", "amp", 0.3)
    test_complex("8[sus2.0 amp4.0||sus0.2]", "sus", 0.4)
