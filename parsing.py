
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

    for i in range( len(string) ):

        char = string[i]
        if char.isdigit():

            if current_symbol == "":
                print("Orphaned digit! Aborting parse...")
                break

            if current_symbol in symbols:
                current_symbol = symbols[current_symbol]
            
            parsing_number += string[i]

        else:
            if parsing_number != "":
                if current_symbol != "tone":
                    parsed_values[current_symbol] = float(parsing_number) / 10.0
                else:
                    parsed_values[current_symbol] = float(parsing_number) # Tone is not split 

                current_symbol = ""
                parsing_number = ""

            current_symbol += char


    if parsing_number != "":
        if current_symbol != "tone":
            parsed_values[current_symbol] = float(parsing_number) / 10.0
        else:
            parsed_values[current_symbol] = float(parsing_number)

        current_symbol = ""
        parsing_number = ""
   
    return parsed_values



print(parse_note("11 arg333 bot87 >15 amp10"))



