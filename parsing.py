
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
        return char.isdigit() or char == "-"


    # 11 = 1.1 (/10) (len 2)
    # 011 = 0.11 (/100) (len 3)
    # 89 = 8.9 (/10) (len 2)
    # 089 = 0.89 (/100) (len 3)
    # 1 = 1.0 (no split) (len 1)

    # Exponent = len - 1
    
    # 890 = 89.0 # len 3 
    # 089 = 0.89 # len 3 
    # 89 = 8.9 

    def parse_number(num: str) -> float:

        negate = "-" in num
        num = num.replace("-", "")

        leading_zeros = 0
        for char in num: 
            if char == "0":
                leading_zeros += 1
            else: 
                break

        length = len(num)
        exponent = 1
        if leading_zeros > 0:
            exponent = length - 1

        base = float(num)
        denominator = 10.0 ** exponent

        if denominator < 1.0:
            denominator = 1.0

        dimension = 1.0
        if negate:
            dimension = -1.0

        if base == 0.0 or length == 1:
            return base 
        else:
            return (base / denominator) * dimension

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

    sus_assert(">015", 0.15)
    sus_assert(">15", 1.5)
    sus_assert(">10", 1.0)
    sus_assert(">0111", 0.111)
    sus_assert(">1", 1.0)
    sus_assert(">0", 0.0)
