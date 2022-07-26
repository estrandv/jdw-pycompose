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
    def create_freq_arg(self, scale, octave):
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
   
    return parsed_values

# Recursive function for expanding contained alternations in a sequence (section list)
# Sections separated by "/" constitute an alternation 
# "0 0 (1/2)" means "Run the whole thing twice, picking 1 on the first and 2 on the second"
# It gets more complex with nested alternations, hence the recursion...  
def expand_alternations(section_list):
    new_list = []

    #print("***** DEBUG: Calling expand on ", " ".join([i.source_text for i in section_list]))

    highest_nested_alternation_index = -1

    for section in section_list:
        # Top level alternations serve no purpose; outcome is the same as space
        if section.separator == "/":
            section.separator = " "
        
        # Highest index of available next-level alternations is the minimum amount
        # of repetitions of the source set we will have to perform to represent everything  
        if (len(section.get_alternations())-1) > highest_nested_alternation_index:
            highest_nested_alternation_index = len(section.get_alternations())-1

    if highest_nested_alternation_index == -1:
        # Bottom of recursion reached; no sections on next level have alternations 
        #print("DEBUG: picked full (non-alt):", " ".join([i.stringify() for i in section_list]))

        return section_list
    else:
        # NOTE: Bit of tweaking with the indices here since modulo behaviour
        # isn't what we want if dealing with actual indices near zero
        # This part iterates through the whole set, building a new expanded set
        # by picking the iteration-matching alternations for each step. 
        for i in range(1, highest_nested_alternation_index + 2):
            for section in section_list:
                max_index = len(section.get_alternations())
                #print("Evaluating section: ", section.source_text)
                if max_index > 0:
                    rem = (i % max_index) - 1
                    this_alternation = section.get_alternations()[rem]
                    #if not this_alternation:
                        #print("ERROR: Empty alternation returned for index ", rem, section.get_alternations())
                    for alt_sec in this_alternation:
                        #print(">> DEBUG: picked from sec ", alt_sec.source_text)
                        new_list.append(alt_sec)
                else:
                    #print(">> DEBUG: picked non-alternating:", section.source_text)
                    # Some sections have no alternations at all and can be kept as-is
                    new_list.append(section)
    
        #print("DEBUG: proceeding with built list:", " ".join([i.stringify() for i in new_list]))
    
        return expand_alternations(new_list)
        


# Sections form a tree structure where the end-node is a single-char representation
# such as "0" or "0[args...]"
class Section:

    # Reconstruct into a similar format as source_string for verification 
    def rebuild_source(self):
        if self.atomic:
            return self.source_text + self.get_arg_string()
        else:
            base = ""
            for section in self.sections:

                base += section.separator 
                if not section.atomic:
                    base += "("
                base += section.rebuild_source()
                if not section.atomic:
                    base += ")"
            return base.replace("( ", "(") # TODO: REally should be centralized 

    def stringify_full(self):
        base = self.source_text 
        
        if self.sections:
            base += "->{" + ",".join([i.stringify_full() for i in self.sections]) + "}" 
            
        base += self.get_arg_string()
        return base 

    def stringify(self):

        base = " ".join([i.stringify() for i in self.sections]) + \
            self.get_arg_string()
        return base 

    def to_debug(self):
        return "'" + self.separator + "'" + "(" + self.stringify() + ")"

    # Fetch all variations on this level as list of lists (but no more levels than that!)
    # For example: 0 / 1 / 4 has 3 variations, 0 (1 / 2 / 3) has 1 (parenthesis is next level)
    def get_alternations(self):
        alternation_list = []
        ongoing_alt = []
        for section in self.sections:
            if section.separator == "/":
                if ongoing_alt:
                    alternation_list.append(ongoing_alt.copy())
                    ongoing_alt = []
            ongoing_alt.append(section)
        if ongoing_alt: 
            alternation_list.append(ongoing_alt.copy())
            ongoing_alt = []

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

    def __init__(self, text, separator = "", common_args = {}):
        # By containing the parsing in the constructor we make subsequent calls easier
        self.separator = separator # "space", "slash" or "root"; what came before this section
        self.sections = [] # Begin list, add new sections through parsing 
        self.atomic_content = "" # Only end-branches have this
        self.args = common_args
        self.source_text = text

        #print("DEBUG: Begin parsing section from ", text)

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
            if self._ongoing_section != "":
                parsed_args = parse_args(self._ongoing_args)

                # Note that we combine the parsed args with the common ones on each level
                # Since a section contained inside another section inherits the args via () 
                for key in common_args:
                    parsed_args[key] = common_args[key]

                self._ongoing_args = ""
                #print("DEBUG: closing and parsing partial section: ", self._ongoing_section, "for level", self.source_text)
                next_sec = Section(self._ongoing_section, self._latest_found_separator, parsed_args)
                self._ongoing_section = ""
                self.sections.append(next_sec)
                #print("DEBUG: Current level structure: ", self.stringify_full())
            #else: # NOTE: Last char close always results in empty

        # The end branches of the recursion will have no separators or special chars 
        self.atomic = True
        for sep in ["[", "(", "/", " "]:
            if sep in text:
                self.atomic = False 

        if self.atomic:
            # Atomic branches need no further step-parsing
            self.atomic_content = text
            #print("DEBUG: Skipping parsing for atomic element ", text)
        else:

            # Example: 0 0 (2/3) 0
            # "2/3" gets passed into close_section() and then Section() without parenthesis
            

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
        result = Section(source).rebuild_source()
        assert expected == result, "bad arg collapse: " + result + " != (expected) " + expected
        print(source + " args collapsed OK")

    test_arg_collapse("0 (0 1)[arg0.0]", "0 (0[arg0.0] 1[arg0.0])")
    test_arg_collapse("0 (0/1)[arg0.0]", "0 (0[arg0.0]/1[arg0.0])")
    test_arg_collapse("(0 (0 1)[arg0.0])[art0.1]", "(0[art0.1] (0[arg0.0 art0.1] 1[arg0.0 art0.1]))")

    def test_expand(source, expected):
        section = Section(source)
        expanded_sections = expand_alternations(section.sections)
        expanded = " ".join([i.source_text for i in expanded_sections]) 
        assert expected == expanded, "bad expand: " + expanded + " != (expected) " + expected
        print(source + " expand-tested OK")

    test_expand("0 t (1/2)", "0 t 1 0 t 2")    
    test_expand("0 0 0 0", "0 0 0 0")    
    test_expand("0 0 (1/2/3)", "0 0 1 0 0 2 0 0 3")    
    test_expand("0 ((1/4)/2)", "0 1 0 2 0 4 0 2")   
    test_expand("0 (1/(2/3))", "0 1 0 2 0 1 0 3")    
    test_expand("0 0 (1/(2/3))", "0 0 1 0 0 2 0 0 1 0 0 3")    

    
    def test_combo(source, expected):
        seed = Section(source).rebuild_source()
        section = Section(seed)
        expanded_sections = expand_alternations(section.sections)
        expanded = " ".join([i.rebuild_source() for i in expanded_sections]) 
        assert expected == expanded, "bad expand/collapse combo: " + expanded + " != (expected) " + expected
        print(source + " expand-tested OK")

    test_combo("hum (dum/(jum/bum))[fum22.0]", "hum dum[fum22.0] hum jum[fum22.0] hum dum[fum22.0] hum bum[fum22.0]")
    test_combo("(0[i55.0] (0/2))[o22.0]", "0[i55.0 o22.0] 0[o22.0] 0[i55.0 o22.0] 2[o22.0]")
