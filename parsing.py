
symbols = {
    "=":"reserved_time",
    ">":"sus",
    "#": "amp"
}


def parse_note(string: str) -> dict[str, float]:

    string = string.replace(" ", "")

    parsed_values: dict[str, float] = {}

    current_symbol = "tone" # Tone is implicit first symbol

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



if __name__ == "__main__":
    print(parse_note("11 arg-333 bot0087 >15 amp08"))
    
    def sus_assert(string: str, expected_sus: float):
        result = parse_note("1 " + string)
        assert expected_sus == result["sus"], "Bad sus: " + str(result["sus"])

    sus_assert(">0.15", 0.15)
    sus_assert(">1.5", 1.5)
    sus_assert(">1.0", 1.0)
    sus_assert(">0.111", 0.111)
    sus_assert(">1", 1.0)
    sus_assert(">0", 0.0)
    sus_assert(">.2", 0.2)
