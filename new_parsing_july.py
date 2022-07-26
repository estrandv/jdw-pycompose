# Rewrite of the string level stuff done in july 2022
# Plan is to make this a completely self-contained parsing package 
# with solid, hackless, well-documented and well-tested code

from scales import transpose
from pretty_midi import note_number_to_hz

# Core class for atomic parts data, such as e.g. a single "note on" with args  
class Message: 

    # When parsing a section string as a Message:
    # prefix: any letters before number or symbol, e.g. "fra" in "fra0" or "fra:" or "fra0:"
    # index: first contained integer, e.g. "12" in "fra12:"
    # symbol: special char right after first number or prefix, if any, e.g. ":" in "0:"
    # suffix: any remaining chars after the index and symbol, e.g. ":!g" in "pre::!g"
    def __init__(self, prefix, index, symbol, suffix, args = {}):
        self.prefix = prefix # Can be None 
        self.index = index # Can be None 
        self.symbol = symbol # Can be None 
        self.suffix = suffix # Can be None 
        self.args = args
    
    # Use index to add a midi-tone-based "freq"-arg to contained args  
    def create_freq_arg(scale, octave):
        if self.index and self.index > 0:
            extra = (12 * (octave + 1)) if octave > 0 else 0
            new_index = self.index + extra
            freq = note_number_to_hz(transpose(new_index, scale))
            self.args["freq"] = freq

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

# TODO: DOcument 
# TODO: I really think it works now! But it needs to be usable within a section. 
def expand_alternations(section_list):
    new_list = []

    highest_nested_alternation_index = -1

    for section in section_list:
        # Top level alternations serve no purpose; outcome is the same as space
        if section.separator == "/":
            section.separator = " "
        
        # Highest index of available next-level alternations is the minimum amount
        # of repetitions we will have to perform to represent everything  
        if (len(section.get_alternations())-1) > highest_nested_alternation_index:
            highest_nested_alternation_index = len(section.get_alternations())-1

    if highest_nested_alternation_index == -1:
        # Bottom of recursion reached; no sections on next level have alternations 
        return section_list
    else:
        # Bit of tweaking with the indices here since modulo behaviour
        # isn't what we want if dealing with actual indices near zero
        for i in range(1, highest_nested_alternation_index + 2):
            for section in section_list:
                max_index = len(section.get_alternations())
                if max_index > 0:
                    rem = (i % max_index) - 1
                    #print("i", i, "max index", max_index,"rem", rem, "section", section.__str__())
                    this_alternation = section.get_alternations()[rem]
                    #print("picked:", [i.__str__() for i in this_alternation])
                    for alt_sec in this_alternation:
                        new_list.append(alt_sec)
                else:
                    # Some sections have no alternations at all and can be kept as-is
                    new_list.append(section)
    
        #print("Half-way: ", [i.__str__() for i in new_list])    
        return expand_alternations(new_list)
        


# Sections form a tree structure where the end-node is a single-char representation
# such as "0" or "0[args...]"
class Section:

    def stringify(self):

        base = self.source_text + " ".join([i.stringify() for i in self.sections]) + \
            self.get_arg_string()
        return base 

    # Fetch all variations on this level as list of lists (but no more levels than that!)
    # For example: 0 / 1 / 4 has 3 variations, 0 (1 / 2 / 3) has 1 (parenthesis is next level)
    def get_alternations(self):
        alternation_list = []
        ongoing_alt = []
        for section in self.sections:
            if section.separator == "/":
                #print("section", section.source_text, "has / as separator", [s.source_text for s in ongoing_alt])
                #print("/ in source set ", self.source_text ,"saving",[a.source_text for a in ongoing_alt])
                alternation_list.append(ongoing_alt.copy())
                ongoing_alt = []
            ongoing_alt.append(section)
        if ongoing_alt: 
            #print("closing source set ", self.source_text ,"saving",[a.source_text for a in ongoing_alt])
            alternation_list.append(ongoing_alt.copy())
            #print("final append: ", [s.source_text for s in ongoing_alt])

        #print(self.source_text, "has", [i.__str__() for y in alternation_list for i in y])
        return alternation_list

    def get_arg_string(self):
        compiled = "" 
        if self.args:
            compiled += "["
            arg_arr = []
            # TODO: No support at all for any rel-args or suchlike
            for key in self.args:
                arg_arr.append(key + str(self.args[key]))
            compiled += " ".join(arg_arr)
            compiled += "]"
        return compiled

    # Rebuild the original string with ()-section-wide args moved into the atomic end-branches 
    # (0 0)[arg0.0] => 0[arg0.0] 0[arg0.0]
    def collapse_arg_tree(self):
        compiled = ""
        
        if self.atomic:
            compiled += self.atomic_content
            if self.args:
                compiled += self.get_arg_string()
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
            #print("Attempting to close section: ", self._ongoing_section, "with sep \'"+ self._latest_found_separator + "\'")
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
                    if self._opened_section_brackets > 0:
                        self._ongoing_section += ch
                    self._opened_section_brackets += 1
                elif ch == ")":
                    self._opened_section_brackets -= 1
                    if self._opened_section_brackets > 0:
                        self._ongoing_section += ch
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

    def test_arg_collapse(source, expected):
        result = Section("", source).collapse_arg_tree()
        assert expected == result, "bad arg collapse: " + result + " != (expected) " + expected
        print(source + " args collapsed OK")

    test_arg_collapse("0 (0 1)[arg0.0]", "0 (0[arg0.0] 1[arg0.0])")
    test_arg_collapse("0 (0/1)[arg0.0]", "0 (0[arg0.0]/1[arg0.0])")
    test_arg_collapse("(0 (0 1)[arg0.0])[art0.1]", "(0[art0.1] (0[arg0.0 art0.1] 1[arg0.0 art0.1]))")

    def test_expand(source, expected):
        section = Section("", source)
        expanded_sections = expand_alternations(section.sections)
        expanded = " ".join([i.stringify() for i in expanded_sections]) 
        assert expected == expanded, "bad expand: " + expanded + " != (expected) " + expected
        print(source + " expand-tested OK")

    test_expand("0 t (1/2)", "0 t 1 0 t 2")    
    test_expand("0 0 (1/2/3)", "0 0 1 0 0 2 0 0 3")    
    test_expand("0 ((1/4)/2)", "0 1 0 2 0 4 0 2")    
    test_expand("0 (1/(2/3))", "0 1 0 2 0 1 0 3")    
    test_expand("0 0 (1/(2/3))", "0 0 1 0 0 2 0 0 1 0 0 3")    

    
