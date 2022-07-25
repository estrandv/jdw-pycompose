# Rewrite of the string level stuff done in july 2022
# Plan is to make this a completely self-contained parsing package 
# with solid, hackless, well-documented and well-tested code


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

# Sections form a tree structure where the end-node is a single-char representation
# such as "0" or "0[args...]"
class Section:

    def __str__(self):

        base = "[" + "separator: " + self.separator + ", " + "content: "

        if self.atomic:
            return base + self.atomic_content + "]"
        else:
            ret = ""
            for sec in self.sections:
                ret += ", " + sec.__str__()
            return base + ret + "]"

    # Rebuild the original string with ()-section-wide args moved into the atomic end-branches 
    # (0 0)[arg0.0] => 0[arg0.0] 0[arg0.0]
    def collapse_arg_tree(self):
        compiled = ""
        
        if self.atomic:
            compiled += self.atomic_content
            if self.args:
                compiled += "["
                arg_arr = []
                # TODO: No support at all for any rel-args or suchlike
                for key in self.args:
                    arg_arr.append(key + str(self.args[key]))
                compiled += " ".join(arg_arr)
                compiled += "]"
            return compiled
        else:
            ret = ""

            for sec in self.sections:

                # TODO: WIP handling of pass-down args 
                if self.args:
                    for key in self.args:
                        sec.args[key] = self.args[key] 

                if sec.atomic:
                    ret += sec.separator + sec.collapse_arg_tree()
                else:
                    ret += sec.separator + "(" + sec.collapse_arg_tree() + ")"
                    # TODO: First atomic in a ()-section will add too much sep 
                    # This is a hack to fix that, I'm sure there's a structural 
                    # way to fix this properly
                    ret = ret.replace("( ", "(").replace("(/", "(")
                    
            return ret 


    def __init__(self, separator, text, common_args = {}):
        # By containing the parsing in the constructor we make subsequent calls easier
        self.separator = separator # "space", "slash" or "root"; what came before this section
        self.sections = [] # Begin list, add new sections through parsing 
        self.atomic_content = "" # Only end-branches have this
        self.args = common_args
        self.source_text = text

        # NOTE: Trailing separators look nice but mess with compiler
        # Thus the hack:
        text = text.replace("  ", " ").replace(" /", "/").replace("/ ", "/")\
            .replace("( ", "(").replace(" )", ")")

        # NOTE: private class args for convenience during this function,
        # not actually needed for anything else

        # To help find the outer-most parenthesis start and end when traversing the chars
        self._opened_section_brackets = 0
        self._opened_arg_brackets = 0

        # Slapped into sections when considered complete, then reset to be filled again
        self._ongoing_section = ""
        # Similar but for []-brackets when chewing through args
        self._ongoing_args = ""

        # Space or slash - saved when one is encountered to be used as separator arg for the
        # next finished section 
        self._latest_found_separator = separator

        # Helper function to close save an ongoing section parse in self.sections         
        def close_section():
            print("Attempting to close section: ", self._ongoing_section, "with sep \'"+ self._latest_found_separator + "\'")
            if self._ongoing_section != "":
                parsed_args = parse_args(self._ongoing_args) 
                # TODO: Multi-level provided args combination 
                self._ongoing_args = ""
                next_sec = Section(self._latest_found_separator, self._ongoing_section, parsed_args)
                self._ongoing_section = ""
                self.sections.append(next_sec)
            else:
                print("ERROR: Attempted to close empty section (or simply last char...)")

        # The end branches of the recursion will have no separators or special chars 
        self.atomic = True
        for sep in ["[", "(", "/", " "]:
            if sep in text:
                self.atomic = False 

        if self.atomic:
            # Atomic branches need no further step-parsing
            self.atomic_content = text
        else:

            for ch in text:

                if ch == "(":
                    self._opened_section_brackets += 1
                elif ch == ")":
                    self._opened_section_brackets -= 1
                    # Ongoing section will be ended on next separator, see below
                    if self._opened_section_brackets < 0:
                        print("ERROR: Too many closing )")
                elif ch == "[":
                    if self._opened_section_brackets == 0: # Parsing of args inside a () will happen in that recursive section's parsing
                        self._opened_arg_brackets += 1
                        if self._opened_arg_brackets > 1:
                            print("ERROR: Nested []-brackets in parse-string!")
                    else:
                        self._ongoing_section += ch
                elif ch == "]":
                    if self._opened_section_brackets == 0:
                        self._opened_arg_brackets -= 1
                        if self._opened_arg_brackets < 0:
                            # Ongoing arg string will be parsed on next separator, see below 
                            print("ERROR: Too many closing ]")
                    else:
                        self._ongoing_section += ch
                elif ch in [" ", "/"]:
                    # Separators mark the end of a section where we reset ongoing read-vars
                    # and send the section into another recursion level.
                    # Note how this applies for both atomic and non-atomic subsections. 
                    if self._opened_arg_brackets == 0 and self._opened_section_brackets == 0:
                        close_section()
                        self._latest_found_separator = ch
                    else:
                        self._ongoing_section += ch 
                else: 
                    # If specifically parsing args we only write those 
                    if self._opened_section_brackets == 0 and self._opened_arg_brackets > 0:
                        self._ongoing_args += ch
                    else:
                        self._ongoing_section += ch

            # Close any remaining 
            close_section()


if __name__ == "__main__":

    print("\"" + Section("", "0  gg[ arg0.0] 0 ( 0[arp0.2] / 1)[arg1.2]").collapse_arg_tree() + "\"")

    #test1 = Section("", "0 0 (0 1/0 2) 0[yahoo]")
    #print(test1)