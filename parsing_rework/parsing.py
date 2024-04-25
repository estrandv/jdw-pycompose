from util import Cursor, TreeExpander
from element import Element, ElementType
import json 
from dataclasses import dataclass
import pytest 
from decimal import Decimal

@dataclass
class SuffixInfo:
    freetext: str = ""
    arg_source: str = ""

# Parse [freetext]:[args] part of element info 
def parse_suffix(suffix_string) -> SuffixInfo:

    cursor = Cursor(suffix_string)
    freetext = cursor.get_until(":")
    cursor.move_past_next(":")
    arg_source = "" if cursor.is_done() else cursor.get_remaining() 
    
    info = SuffixInfo() 
    info.freetext = freetext
    info.arg_source = arg_source
    return info 

@dataclass
class SuffixFreetextInfo:
    repeat: int = 1

# Parse non-arg part of suffix string
# ATM only "xN" for repeat! 
def parse_suffix_freetext(suffix_freetext) -> SuffixFreetextInfo:
    cursor = Cursor(suffix_freetext)
    info = SuffixFreetextInfo() 
    if not cursor.is_done() and cursor.get() == "x":
        cursor.next() 
        if not cursor.is_done():
            numeric = cursor.get_remaining()
            if numeric != "":
                info.repeat = int(numeric)

    return info 

# Parse 1.0,arg2,argb2.0 [...] part of element info suffix 
def parse_args(arg_source) -> dict:
    args = {}

    cursor = Cursor(arg_source)
    while True: 
        # Step on separator at a time 
        content = cursor.get_until(",")

        sub_cursor = Cursor(content)
        non_numeric = sub_cursor.get_until("0123456789")

        # Step into the numeric part of the string unless it began immediately 
        if sub_cursor.peek() != "" and non_numeric != "":
            sub_cursor.next()

        numeric = sub_cursor.get_remaining()

        if numeric != "": 
            numeric_decimal = Decimal(numeric)

            if non_numeric == "":
                if len(args) == 0:
                    # TODO: Some other way to provide this default 
                    # First arg is "time" unless otherwise noted 
                    args["time"] = numeric_decimal
                else:
                    raise Exception("Parsing error: unnamed arg")
            else:
                args[non_numeric] = numeric_decimal

        cursor.move_past_next(",")
        if cursor.is_done():
            break 

    return args 

# Top level division of elements - ()-sections, /-alternations and "abc123"-atomics 
def parse_sections(source_string) -> Element:
    cursor = Cursor(source_string)
    master_section = Element()
    master_section.type = ElementType.SECTION
    current_element = master_section 

    while True:
        if cursor.get() == "(":
            current_element = current_element.add()
            current_element.type = ElementType.SECTION
        elif cursor.get() == ")":
            cursor.next()
            if not cursor.is_done():
                current_element.information = cursor.get_until(" ")

            # Convoluted because alternations create nested parents 

            if current_element.parent == None: 
                raise Exception("Encountered closing bracket in section with no parent (orphaned closing bracket?)")
            if current_element.parent.type == ElementType.ALTERNATION_SECTION:
                if current_element.parent.parent == None:
                    raise Exception("Encountered closing bracked in alternation section with no grandparent (orphaned closing bracket?)")
                current_element = current_element.parent.parent 
            else:  
                current_element = current_element.parent 
        elif cursor.get() == "/":        

            if current_element.parent != None and current_element.parent.type == ElementType.ALTERNATION_SECTION:
                current_element = current_element.parent.add() 
                current_element.type = ElementType.SECTION
            else:
                # Create an inbetween alternation parent 
                # Nest the ongoing section under it as a new section 
                downport = current_element.elements
                current_element.elements = []
                current_element.type = ElementType.ALTERNATION_SECTION
                nest = current_element.add()
                nest.elements = downport
                nest.type = ElementType.SECTION
                for ele in nest.elements:
                    ele.parent = nest

                # Begin new section after the slash 
                current_element = current_element.add() 
                current_element.type = ElementType.SECTION  
            
        elif cursor.get() != " ":
            current_element = current_element.add()
            current_element.type = ElementType.ATOMIC
            current_element.information += cursor.get_until(") ")
            current_element = current_element.parent 

        if cursor.peek() == "":
            break
        else:
            cursor.next()

    return master_section     

# Run tests if ran standalone 
if __name__ == "__main__": 

    # Perform some bad faith tests
    with pytest.raises(Exception) as x:
        parse_sections(")))")
        assert "orphaned closing bracket" in x.value
        assert "no parent" in x.value

    # These should be OK even if they are gibberish 
    parse_sections("                ")
    parse_sections("(a c v")
    parse_sections("(((((/)))))")

    def assert_type(element, type):
        assert element.type == type, element.type 

    atomic_test = parse_sections("a")
    assert atomic_test.type == ElementType.SECTION, atomic_test.type
    assert len(atomic_test.elements) == 1, len(atomic_test.elements)
    assert atomic_test.elements[0].type == ElementType.ATOMIC, atomic_test.elements[0].type

    single_alt_test = parse_sections("a / b / c / d")
    assert_type(single_alt_test, ElementType.ALTERNATION_SECTION)
    assert len(single_alt_test.elements) == 4, len(single_alt_test.elements)

    nested_alt_test = parse_sections("a b c / (a (b / b2) c / d d) c")
    assert_type(nested_alt_test, ElementType.ALTERNATION_SECTION)
    assert len(nested_alt_test.elements) == 2, len(nested_alt_test.elements)
    assert_type(nested_alt_test.elements[1], ElementType.SECTION)
    assert_type(nested_alt_test.elements[1].elements[0], ElementType.ALTERNATION_SECTION)
    abc_nest = nested_alt_test.elements[1].elements[0].elements[0]
    assert_type(abc_nest, ElementType.SECTION)
    assert len(abc_nest.elements) == 3, len(abc_nest.elements)

    alternation_count_test = parse_sections("b (c / d / (e / f)").alternation_count()
    assert alternation_count_test == 6, alternation_count_test

    # Quick assertion of atomic elements after a full tree alternations expand    
    # TODO: Tree expander should have its own tests, not get mixed up with parsing
    # This is a lot easier for now though ...     
    tree_expand_test = parse_sections("a (b / (p f / (d / h))")
    tree = TreeExpander()
    tree_expand_string = ",".join([e.information for e in tree.tree_expand(tree_expand_test)])
    assert tree_expand_string == "a,b,a,p,f,a,b,a,d,a,b,a,p,f,a,b,a,h"

    # TODO: Future staring here. Safe, step-by-step procedure to include parent args
    # Best if this is done before unwrapping, in case alternations want different uses
    nested_arg_set = parse_sections("f (( ::a )b )c")
    assert len(nested_arg_set.elements) == 2
    a_node = nested_arg_set.elements[1].elements[0].elements[0]
    assert a_node.get_information_array_ordered() == ["::a", "b", "c", ""], "was: " + ",".join([a for a in a_node.get_information_array_ordered()])

    # TODO: With a way to unwrap, and a way to resolve parent args, we can start working on the atomic parse 
    # This parse will parse (1) core symbols and indices (2) optional arg string at the end
    # Resolve other todos first to ensure a clean codebase 

    # Suffix tests 

    # TODO: Consider separate files for separate parts of parsing logic 
    suffix_test_simple = parse_suffix("abc:1.0,fc33")
    assert suffix_test_simple.arg_source == "1.0,fc33", suffix_test_simple.arg_source
    assert suffix_test_simple.freetext == "abc", suffix_test_simple.freetext

    suffix_test_no_args = parse_suffix("()---")
    assert suffix_test_no_args.arg_source == "", suffix_test_no_args.arg_source
    assert suffix_test_no_args.freetext == "()---", suffix_test_no_args.freetext

    suffix_broken_args_test = parse_suffix("f:")
    assert suffix_broken_args_test.freetext == "f", suffix_broken_args_test.freetext 
    assert suffix_broken_args_test.arg_source == "", suffix_broken_args_test.arg_source

    # Args tests 

    no_arg_test = parse_args("")
    assert len(no_arg_test) == 0

    arg_test_basic = parse_args("1.0")
    assert arg_test_basic["time"] == Decimal("1.0"), arg_test_basic["time"]
    assert len(arg_test_basic) == 1, len(arg_test_basic)

    arg_test_basic_2 = parse_args("fish1.0,cheese0.3")
    assert "fish" in arg_test_basic_2
    assert "cheese" in arg_test_basic_2
    assert arg_test_basic_2["fish"] == Decimal("1.0"), arg_test_basic_2["fish"]
    assert arg_test_basic_2["cheese"] == Decimal("0.3"), arg_test_basic_2["cheese"]
    
    # TODO: Consider ".2" shorthand support 
    arg_test = parse_args("0.2,;900,lob0.002")
    assert "time" in arg_test
    assert ";" in arg_test
    assert "lob" in arg_test
    assert arg_test["time"] == Decimal("0.2"), arg_test["time"]
    assert arg_test[";"] == Decimal("900"), arg_test[";"]
    assert arg_test["lob"] == Decimal("0.002"), arg_test["lob"]
    
    # Suffix freetext testing 

    freetext_test = parse_suffix_freetext("")
    assert freetext_test.repeat == 1, freetext_test.repeat
    
    freetext_test_2 = parse_suffix_freetext("x44")
    assert freetext_test_2.repeat == 44, freetext_test_2.repeat

    """
        REVISITING THE FEATURE SPEC: 
        1. Complete reconstruction (know what was entered, interpret things like alternations freely at later time).
        2. SYNTAX

            d3:1.0,mut2.0,arg0.1 e3 ((a3 / b2) b3):0.2
    
            - csv args (after ":" or other spacer), to simplify writing and sanctify whitespace as note-spacing
                - "time" as convenience arg; naming not necessary
            - first class parentheses, where everything written directly after is interpreted as for notes
            - same old atomic note split: 
                [prefix: non-number string] [index: number] [suffix: non-number string] [args: sub-parse if arg-symbol (always last)]
        3. Alternation needs 
            - (a b c (d/f))x8 should single-resolve for each "x", rather than unpack everything eight times
                -> a b c d a b c f [...]
            
            => THIS IS TRICKY TO KEEP IN YOUR HEAD 
                - Default interpretation is "repeat until unwrapped everything", so behaivour gets a bit mixed
        
                    a b c (d/f) -> a b c d a b c f

                    a b c (d/f)x2 -> a b c d f a b c d f (rather than single-iteration "spend the whole thing")

                    Ideally, expand_alternations should count how many times an alternation is ticked and be satisfied when it has expanded all contained items. 

                    I think you can get around this by tinkering with alternation_count:
                        - if xN, return max count divided by N

                    REQUIREMENT: Repeat amount known early
                        - Extra tricky because it propagates downward 
                        - Better, then, to resolve args BEFORE alternation unwrapping
                            -> Somewhat easy if dynamic to start with
            

            CONCLUSION:
                - Start with "parse_suffix" which can detect both args and repeats 
                - Make sure it returns complete information 

            4. REMEMBER: We want proper syntax error handling this time as well 
            5. Once all parsing is solid, we can move on to OSC transformation 

    """