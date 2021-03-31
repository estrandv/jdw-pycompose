
symbols = {
    "=":"reserved_time",
    ">":"sus",
    "#": "amp"
}


def parse_note(string: str) -> dict[str, float]:

    string = string.replace(" ", "")

    tone: int = int(string[0:2])

    post_tone: str = string[2:]
    
    parsed_values: dict[str, float] = {"tone": tone}

    current_symbol = ""

    parsing_number = ""

    for i in range( len(post_tone) ):

        char = post_tone[i]
        if char.isdigit():

            if current_symbol == "":
                print("Orphaned digit! Aborting parse...")
                break

            if current_symbol in symbols:
                current_symbol = symbols[current_symbol]
            
            parsing_number += post_tone[i]

        else:
            if parsing_number != "":
                parsed_values[current_symbol] = float(parsing_number) / 10.0
                current_symbol = ""
                parsing_number = ""

            current_symbol += char


    if parsing_number != "":
        parsed_values[current_symbol] = float(parsing_number) / 10.0
        current_symbol = ""
        parsing_number = ""
   
    return parsed_values



print(parse_note("11 arg333 bot87 >15 amp10"))



