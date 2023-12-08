# Rewrite of the string level stuff done in july 2022
# Plan is to make this a completely self-contained parsing package 
# with solid, hackless, well-documented and well-tested code

from scales import transpose
from pretty_midi import note_number_to_hz
from fractions import Fraction

# Easy debug logging
debug = False   
def debug_log(message):
    if debug:
        print("DEBUG: " + message)

def note_letter_to_midi(note_string) -> int:
    # https://stackoverflow.com/questions/13926280/musical-note-string-c-4-f-3-etc-to-midi-note-value-in-python
    # [["C"],["C#","Db"],["D"],["D#","Eb"],["E"],["F"],["F#","Gb"],["G"],["G#","Ab"],["A"],["A#","Bb"],["B"]]
    note_map = {
        "c": 0,
        "c#": 1,
        "db": 1,
        "d": 2,
        "d#": 3,
        "eb": 3,
        "e": 4,
        "f": 5,
        "f#": 6,
        "gb": 6,
        "g": 7,
        "g#": 8,
        "ab": 8,
        "a": 9,
        "a#": 10,
        "bb": 10,
        "b": 11
    }

    if note_string in note_map:
        return note_map[note_string]
    else:
        return -1


# See nested methods for documentation. This turns a section-compatible source string
# (e.g. ": 0t (bo2/3)[arg0.0] 0") into a list of sequential messages according to the parsing logic
# in this document. See tests at bottom of file for more examples. 
def full_parse(source: str) -> list["Message"]:

    if source and source[0] == "(":
        print("ERROR: top level brackets not allowed, please unwrap the first and final ()")
        return []

    if source and source[0] == "M":
        print("Mute triggered")
        # Leaving it like this for now since an on-beat mute is better for restarts given the current state of the sequencer. 
        # TODO: Bit of a hidden piece of logic, rework eventually 
        return full_parse("_ :: =1")

    master_args = {}
    master_args_are_relative = False 

    # Master args that apply to all
    if "::" in source:
        marg_split = source.split("::")
        arg_section = marg_split[-1]
        if arg_section != "" and arg_section[0] == ";":
            master_args_are_relative = True 
            arg_section = "".join(arg_section[1:])
        master_args = parse_args(arg_section)
        source = "".join(marg_split[:-1])


    # List of lists 
    messages_by_chunk = []

    # Initial chunk verification due to conflicting functionality with ()-alternations
    open_brackets = 0
    for char in source:
        if char == "(":
            open_brackets += 1
        elif char == ")":
            open_brackets -= 1 
        elif char == "{" and open_brackets > 0:
            print("ERROR: Attempted to split chunk with {} during opened alternation bracket () - this is not allowed!")
            return []

    # Go through separated chunks using the {} syntax 
    chunks = source.split("{") # e.g. "0 0" "> 0 0"

    for chunk in chunks:
        chunk_source = chunk
        if "}" in chunk: # Arg handling required 
            last_end_split = chunk_source.split("}")
            chunk_source = "".join(last_end_split[1:])
            last_chunk_args = parse_args(last_end_split[0])

            # Apply now finished args of last chunk
            if messages_by_chunk and last_chunk_args:
                messages_by_chunk[-1] = apply_meta_args_to_messages(messages_by_chunk[-1], last_chunk_args)               

        # Initial section object created, including unexpanded alternations
        # See: Section object documentation. In short: tree-structure where the end-branches are
        # parseable as Message.
        # NOTE: Boolean-ness of strip() to ensure string is not blank or empty 
        if chunk_source and chunk_source.strip():
            debug_log("Creating section from chunk: " + chunk_source)
            seed = Section(chunk_source)
            # NOTE: This might no longer be required, but doesn't hurt for validation. 
            # Source string is rebuilt after optimizing and then parsed again.
            # UPDATE: This was causing a bug and has been removed without breaking tests. Should be ok? 
            #rgs_collapsed = Section(seed.rebuild_source())
            args_collapsed = seed 

            # Expand into list of atomic sections. 
            atomic_set = flatten_sections([args_collapsed])

            # Create message for each end-branch after expanding/"decompiling". 
            all_messages = [create_message(atom) for atom in atomic_set]

            # Add master args 
            for msg in all_messages:
                if master_args_are_relative:
                    msg.add_relative_args(master_args)
                else:
                    debug_log("Adding missing args " + str(master_args) + " to source " + source)
                    msg.add_missing_args(master_args)

            messages_by_chunk.append(all_messages)

    # Flatten list of lists and return full set 
    return [message for sublist in messages_by_chunk for message in sublist]

def apply_meta_args_to_messages(message_list, args):
    
    ret_list = message_list.copy()
    if "x" in args and args["x"] > 1.0:
        debug_log("Applying the 'x' meta-arg to duplicate messages before it. Copying n messages: " + str(len(message_list)) + " n-1 times: " + str(args["x"]))
        for i in range(0, int(args["x"]) - 1):
            for msg in message_list.copy():
                ret_list.append(msg)

    return ret_list

# Parse an atomic section string (e.g. "pre:su" or "0") into a message object 
def create_message(section: "Section") -> "Message":
    if not section.atomic:
        print("FATAL ERROR: Attempted to parse non-atomic section as Message")

    # No need to get anything but the core text. Args are already parsed and should NOT be 
    # registered by the parser in this function. 
    source = section.source_text
    args = section.args  

    step = "prefix" # Hacky way of handling which part of the message we are currently parsing

    # Symbols that have a specific meaning and can replace numbers as core component
    special_symbols = [
        ":", # "modify" symbol
        "$", # "drone" symbol
        "_" # "break" symbol # TODO: amp logic will have to be handled later 
    ]

    prefix = ""
    number = ""
    symbol = ""
    suffix = ""

    for ch in source:
        if step == "prefix":
            if ch.isdigit():
                step = "number"
                number += ch
            elif ch in special_symbols:
                step = "suffix" # There is no "symbol" step since symbol is only ever one char  
                symbol = ch
            else:
                prefix += ch 
        elif step == "number":
            if ch.isdigit():
                number += ch
            elif ch in special_symbols:
                step = "suffix"
                symbol = ch
            else: 
                step = "suffix"
                if ch in special_symbols:
                    symbol = ch
                else:
                    suffix += ch 
        elif step == "suffix":
            suffix += ch 

    return Message(prefix, int(number) if number else None, symbol, suffix, section.args)

# Core class for atomic parts data that can then be represented as some kind of single message 
# via conversion  
# Seed data is typically an atomic end-branch of the Section class, e.g. "bd22t[arg0.0]" or even "0"
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

    # Multiply existing args with corresponding provided ones
    # Flat add the provided ones if unavailable locally 
    def add_relative_args(self, args):
        for arg in args:
            if arg not in self.args:
                self.args[arg] = args[arg]
            else:
                self.args[arg] *= args[arg]

    def add_missing_args(self, args):
        debug_log("before add-missing, we have this: " + str(self.args))
        for arg in args:
        # 1: prefix will be everything before the index and should scan to a number on the chromatic scale, e.g. C# -> 1 
            if arg not in self.args:
                self.args[arg] = args[arg]
        debug_log("after add-missing, we have this: " + str(self.args))

    def clone(self):
        return Message(self.prefix, self.index, self.symbol, self.suffix, self.args.copy())
    
    # Use index to add a midi-tone-based "freq"-arg to contained args  
    def create_freq_arg(self, scale, octave):
        if self.index and self.index > 0:
            extra = (12 * (octave + 1)) if octave > 0 else 0
            new_index = self.index + extra
            freq = note_number_to_hz(transpose(new_index, scale))
            self.args["freq"] = freq

    # Alternative to "create_freq_arg" where we instead infer notes from typical letter+octave notation 
    def create_letter_freq_arg(self):

        # 1: prefix will be everything before the index and should scan to a number on the chromatic scale, e.g. C# -> 1 
        # 2: index basically sets the octave and should default to 1 or 0 if missing 
        # Steal formula from here: 

        if self.prefix != None:

            # E.g. "C" or "C#" or "Cb"
            letter_and_semitone = self.prefix.lower() 
            # As in the "3" of "c3"
            octave = self.index if self.index != None else 1

            # Math, same as for index freq calculation
            tone = note_letter_to_midi(letter_and_semitone)
            tone_index = 0 if tone == -1 else tone 
            extra = (12 * (octave + 1)) if octave > 0 else 0
            new_index = tone_index + extra

            freq = note_number_to_hz(new_index)
            self.args["freq"] = freq

        pass 


# "amp0.1 sus0.5" -> {"amp": 0.1, "sus": 0.5}
def parse_args(string: str) -> dict[str, float]:


    # Common arg names get the following shorthands for easy typing 
    shorthand_symbols = {
        "=":"time",
        ">":"gate_time",
        "#": "amp",
        "@": "gate"
    }

    # Remove whitespace
    string = string.replace(" ", "")

    parsed_values: dict[str, float] = {}

    current_argname = ""

    parsing_number = ""

    def is_num(char: str) -> bool:
        return char.isdigit() or char == "-" or char == "." or char == "/"

    def parse_number(num: str) -> float:

        negate = "-" in num
        num = num.replace("-", "")

        base = float(Fraction(num))

        dimension = -1.0 if negate else 1.0

        return base * dimension if base != 0.0 else base

    for i in range( len(string) ):

        char = string[i]
        if is_num(char):

            if current_argname == "":
                print("Orphaned digit! Aborting parse...")
                break

            if current_argname in shorthand_symbols:
                current_argname = shorthand_symbols[current_argname]
            
            parsing_number += string[i]

        else:
            if parsing_number != "":
                if current_argname == "tone":
                    parsed_values[current_argname] = float(parsing_number)
                else:
                    parsed_values[current_argname] = parse_number(parsing_number)
                current_argname = ""
                parsing_number = ""

            current_argname += char


    if parsing_number != "":
        parsed_values[current_argname] = parse_number(parsing_number)
        current_argname = ""
        parsing_number = ""
   
    return parsed_values

# Recursive function for expanding contained alternations in a sequence (section list)
# Sections separated by "/" constitute an alternation 
# "0 0 (1/2)" means "Run the whole thing twice, picking 1 on the first and 2 on the second"
# It gets more complex with nested alternations, hence the recursion...  
def flatten_sections(section_list: list["Section"]) -> list["Section"]:
    new_list = []

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
                        new_list.append(alt_sec)
                else:
                    # Some sections have no alternations at all and can be kept as-is
                    new_list.append(section)
    
    
        return flatten_sections(new_list)
        


# Sections form a tree structure where the end-node is a single-char representation
# such as "0" or "0[args...]"
class Section:

    # Reconstruct into a similar format as source_string for verification 
    def rebuild_source(self) -> str:
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

    # Create a string for representing both this section and the recursion chain relationships
    # of its children
    def stringify_full(self) -> str:
        base = self.source_text 
        
        if self.sections:
            base += "->{" + ",".join([i.stringify_full() for i in self.sections]) + "}" 
            
        base += self.get_arg_string()
        return base 

    # Create a simple string represenatation of this section without its children 
    def stringify(self):

        base = " ".join([i.stringify() for i in self.sections]) + \
            self.get_arg_string()
        return base 

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

    # Wrap args dict into a string representation like "[argA0.0, argB1.2, ...]"
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

        debug_log("Begin parsing section from "+ text)

        # NOTE: Trailing separators look nice but mess with compiler
        # Thus the hack:
        text = text.replace("  ", " ").replace(" /", "/").replace("/ ", "/")\
            .replace("( ", "(").replace(" )", ")")

        # Check if a cutoff character exists, ending the parse string prematurely
        # TODO: Collect all symbol chars as constants somewhere for better overview 
        if "§" in text:
            text = text.partition("§")[0]

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
                    # NOTE: No override, only adding missing 
                    if key not in parsed_args:
                        parsed_args[key] = common_args[key]

                self._ongoing_args = ""
                next_sec = Section(self._ongoing_section, self._latest_found_separator, parsed_args)
                self._ongoing_section = ""
                self.sections.append(next_sec)
            #else: # NOTE: Last char close always results in empty

        # The end branches of the recursion will have no separators or special chars 
        self.atomic = True
        for sep in ["[", "(", "/", " "]:
            if sep in text:
                self.atomic = False 

        # Count sequential repeat characters for smooth repeat 
        self.repeats = 0

        if self.atomic:
            # Atomic branches need no further step-parsing
            self.atomic_content = text
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

                    # First handle any open repeats, always 
                    # Note the logic: Sequential repeats will repeat xn
                    # 00 £ £ -> 00 00 00
                    if self.repeats > 0:
                        clone_sec = []
                        for section in self.sections:
                            clone_sec.append(section)
                        for i in range(0, self.repeats):
                            self.sections += clone_sec
                        self.repeats = 0

                    if self._opened_arg_brackets == 0 and self._opened_section_brackets == 0:
                        close_section()
                        self._latest_found_separator = ch
                    else:
                        if self._opened_section_brackets == 0 and self._opened_arg_brackets > 0:
                            self._ongoing_args += ch
                        else:
                            self._ongoing_section += ch

                # Repeat character handling
                # TODO: This repeat char is significantly more hacky than the other stuff and could use 
                # a lot of clarification (for example the other repeat works like ""= = ="" while this is strictly £££)
                elif ch == "£" and self._ongoing_section == "":
                    self.repeats += 1
                elif ch == "#" and self._ongoing_section == "":
                    pass # Empty marker symbol handling 
                else: 
                    # If specifically parsing args we only write those 
                    if self._opened_section_brackets == 0 and self._opened_arg_brackets > 0:
                        self._ongoing_args += ch
                    else:
                        self._ongoing_section += ch

            # Close any remaining 
            close_section()

    


if __name__ == "__main__":

    def test_arg_parse(source, key, value):
        args = parse_args(source)
        assert value == args[key], "Expected parsed arg " + key + " to be " + str(value) + " but was " + str(args[key])

    test_arg_parse("tit0.2", "tit", 0.2)
    test_arg_parse("tit0.2 tat55", "tat", 55.0)
    test_arg_parse("tit0.2 for1/8 tat55", "for", 0.125)

    def test_arg_collapse(source, expected):
        result = Section(source).rebuild_source()
        assert expected == result, "bad arg collapse: " + result + " != (expected) " + expected

    test_arg_collapse("0 (0 1)[arg0.0]", "0 (0[arg0.0] 1[arg0.0])")
    test_arg_collapse("0 (0/1)[arg0.0]", "0 (0[arg0.0]/1[arg0.0])")
    test_arg_collapse("(0 (0 1)[arg0.0])[art0.1]", "(0[art0.1] (0[arg0.0 art0.1] 1[arg0.0 art0.1]))")

    def test_expand(source, expected):
        section = Section(source)
        expanded_sections = flatten_sections([section])
        expanded = " ".join([i.source_text for i in expanded_sections]) 
        assert expected == expanded, "bad expand: " + expanded + " != (expected) " + expected

    test_expand("0 t (1/2)", "0 t 1 0 t 2")    
    test_expand("0 0 0 0", "0 0 0 0")    
    test_expand("0 0 (1/2/3)", "0 0 1 0 0 2 0 0 3")    
    test_expand("0 ((1/4)/2)", "0 1 0 2 0 4 0 2")   
    test_expand("0 (1/(2/3))", "0 1 0 2 0 1 0 3")    
    test_expand("0 0 (1/(2/3))", "0 0 1 0 0 2 0 0 1 0 0 3")    
    test_expand("0 0", "0 0")    
    test_expand("0", "0")    

    
    def test_combo(source, expected):
        seed = Section(source).rebuild_source()
        section = Section(seed)
        expanded_sections = flatten_sections([section])
        expanded = " ".join([i.rebuild_source() for i in expanded_sections]) 
        assert expected == expanded, "bad expand/collapse combo: " + expanded + " != (expected) " + expected

    test_combo("hum (dum/(jum/bum))[fum22.0]", "hum dum[fum22.0] hum jum[fum22.0] hum dum[fum22.0] hum bum[fum22.0]")
    test_combo("(0[i55.0] (0/2))[o22.0]", "0[i55.0 o22.0] 0[o22.0] 0[i55.0 o22.0] 2[o22.0]")

    def verify_message(source, key, val):
        seed = Section(source)
        msg = create_message(seed)
        assert val == msg.__dict__[key], "Message parsing failed: " \
            + key + "='" + str(msg.__dict__[key]) +"' was not '" + str(val) + "'"

    verify_message("0", "index", 0)
    verify_message(":", "symbol", ":")
    verify_message(":", "index", None)
    verify_message("22:", "index", 22)
    verify_message("22:", "symbol", ":")
    verify_message("bo22:t", "prefix", "bo")
    verify_message("b22:t", "index", 22)
    verify_message("bo22:t", "symbol", ":")
    verify_message("bo22:ti", "suffix", "ti")
    verify_message("bo:t", "index", None)
    verify_message("bo:t", "symbol", ":")
    verify_message("c#", "prefix", "c#")
    verify_message("eb", "prefix", "eb")

    # TODO: Even more validation, but for now a simple "didn't crash" will do 
    full_parse("0 : ti22p (0/(2/:[aj22.0])/4)[arg0.0] bi: fish0")
    msgs = full_parse("0 : t22 (2/2)")
    assert len(msgs) == 8, "Wrong amount of messages generated after full_parse: " + str(len(msgs))

    arg_test = full_parse("0[time1.0] 4 5 2[fis1.0]")
    assert 1.0 == arg_test[0].args["time"]

    # Test cutoff 
    cut_test = full_parse("0 0 §0 0 0")
    assert len(cut_test) == 2, "Expected cutoff to end parsing and return 2 messages: " + len(cut_test)

    # Test fractional args inside longer strings
    fractional_test = full_parse("0 0[=1/4] 0")
    assert len(fractional_test) == 3, "Fractional string broken, wrong amount of messages: " + len(cut_test)
    t_arg = fractional_test[1].args["time"]
    assert 0.25 == t_arg, "Fractional parsing in longer string broken: " + str(t_arg)

    # TODO: Nested chunks. If you wrap a parenthesis around top level the chunk splitting will break everything 
    # One way to chicken out is to disallow top level parenthesis and handle master args differently 
    # The alternative is a deep dive in section logic that quickly becomes a recursion headache
    chunk_test = full_parse("0 (1/2) _ {x3} 0 0 0 0 {}")
    assert 22 == len(chunk_test), "Wrong amount of total messages after chunk parse: " + str(len(chunk_test))

    # TODO: If we go for this syntax, it would perhaps be helpful to use ALL available ::-parts if multiple
    # I don't see the use for this in regular writing but it's a good way to ensure defaults, for example 
    # ... or we just manually do defaults by iterating parsed messages 
    master_arg_test = full_parse("0 0[x5] 0 0 :: x3")
    assert 5.0 == master_arg_test[1].args["x"]
    assert 3.0 == master_arg_test[0].args["x"]

    marg_one = full_parse("0 :: =4")
    marg_two = full_parse("1 :: =1")
    assert 4 == marg_one[0].args["time"], "Unexpected time arg " +  str(marg_one[0].args["time"])
    assert 1 == marg_two[0].args["time"], "Unexpected time arg " +  str(marg_two[0].args["time"])

    margtest_2 = full_parse("0 (1/2) :: x3")
    assert 4 == len(margtest_2), "Unexpected unpackged len for alternation with master args: " + str([n.index for n in margtest_2])

    margtest_3 = full_parse("0[x5.0] ::; x0.5")
    assert 2.5 == margtest_3[0].args["x"], "Relative master args did not apply correctly: " + str(margtest_3[0].args["x"])

    # Should error and abort 
    catchem_test = full_parse("0 0 (1 2 (1/3) {x5} _) 2")
    assert 0 == len(catchem_test)

    # From real error scenario
    multi_len_test = full_parse("6 {x7} 7 {x8} :: fish0.2")
    for msg in multi_len_test:
        debug_log("Message created " + str(msg.__dict__))
    assert 15 == len(multi_len_test), "Unexpexted length of parsed messages: " + str(len(multi_len_test))


    # TODO: Rel args
    # - Noted that a certain kind of master arg could probably be used to relativize all contained args post-fact 
    # - A message could have "apply_relative" as a method 
    # - So "0 0[1/2] 4 ;; 1/8" would take the 1/8 flat if unavailable or multiplied if not 
    # - Basically just a slightly different "use if not available"
    relarg_test = full_parse("1[=1/2] 2 3 4 ::; =1/2")
    assert 0.25 == relarg_test[0].args["time"], str(relarg_test[0].args["time"]) + " with args " + str(relarg_test[0].args)


    # Letter notation 

    def verify_tone(source, expect_freq):
        seed = Section(source)
        msg = create_message(seed)
        msg.create_letter_freq_arg()
        assert expect_freq == msg.args["freq"], "Letter-note inferrence failed: " \
            + "freq" + "='" + str(msg.args["freq"]) +"' was not '" + str(expect_freq) + "'"

    verify_tone("a4", 440.0)
    verify_tone("c", 32.70319566257483)
    verify_tone("gb3", 184.9972113558172)
    verify_tone("b8", 7902.132820097988)
    

    print("All parsing tests OK")
