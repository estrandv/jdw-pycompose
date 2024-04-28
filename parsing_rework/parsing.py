import util 
from cursor import Cursor
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

def parse_sections(source_string) -> Element:
    
    current_element = Element()
    current_element.type = ElementType.SECTION 

    def store(element):
        if current_element.type == ElementType.ALTERNATION_SECTION:
            current_alternation.append(element)
        else:
            current_element.elements.append(element)
            element.parent = current_element

    def end_current_alternation(alternation):

        if len(alternation) > 1:
            sub_section = current_element.add()
            sub_section.type = ElementType.SECTION
            
            for ele in alternation:
                ele.parent = sub_section
                sub_section.elements.append(ele)
        else:
            # Looped to be 0-len safe, although typically one element 
            for ele in alternation:
                ele.parent = current_element
                current_element.elements.append(ele)


    # Divide into substrings, separated by space unless bracketed
    # Dealing with one bracket-layer at a time 
    current_alternation = []
    for substring in util.section_split(source_string):

        if "(" in substring or ")" in substring:

            # Grab meta-information and then recursively parse bracketed sections 

            if substring[0] != "(":
                raise Exception("Malformed input - section does not start with '(' :" + substring)

            # TODO: Suffix should be allowed to contain ")" - we should not look for the last index
            #   but for the index of when all parentheses have been closed. 
            end_index = substring.rfind(")")

            if end_index == -1:
                raise Exception("Malformed input - section does not have an ending ')': " + substring)

            # Perform information gathering 
            end_information = "".join(substring[end_index + 1:]) if substring[-1] != ")" else ""

            unwrap = "".join(substring[1:end_index])
            #print("Unwrapped a bracket", substring, "into", unwrap, "with information", end_information)

            sub_section = parse_sections(unwrap)
            sub_section.information = end_information
            #print("Storing subsection", unwrap, "<< as >>", sub_section.represent())
            store(sub_section)

        elif substring == "/":

            if current_element.type == ElementType.ALTERNATION_SECTION:

                if len(current_alternation) == 0:
                    raise Exception("Malformed input - possible duplicate '/':")

                # Not the first encountered / 
                # Take all elements created since the last /
                # Add them as a section if multiple 
                
                end_current_alternation(current_alternation) 
                current_alternation = []

            elif len(current_element.elements) > 0: 
                # Classify ongoing section as alternation
                # Move any previously passed elements into a subsection (if plural)
                current_element.type = ElementType.ALTERNATION_SECTION
                current_alternation = []
                
                if len(current_element.elements) > 1:
                    port = current_element.elements 
                    sub_section = Element()
                    sub_section.type = ElementType.SECTION
                    sub_section.elements = port
                    for e in sub_section.elements:
                        e.parent = sub_section
                    current_element.elements = [sub_section]
                    
            else:
                raise Exception("Malformed input - '/' written before any other elements in section")
        else:
            # Regular, atomic entry 
            atomic = Element() 
            atomic.type = ElementType.ATOMIC
            atomic.information = substring

            store(atomic)

    # In case last element is part of an alternation (post-/)
    end_current_alternation(current_alternation)
    current_alternation = []
    
    return current_element

# Run tests if ran standalone 
if __name__ == "__main__": 

    # This should be OK, even if gibberish 
    parse_sections("                ")

    def test_malformed_input(inp):
        with pytest.raises(Exception) as exc_info:   
            parse_sections(inp)
            assert "Malformed input" in exc_info.value

    test_malformed_input("(a c v")
    test_malformed_input("(((((/)))))")
    test_malformed_input("a / / b")

    def representation_test(source):
        res = parse_sections(source).represent()
        assert res == "(" + source + ")", res 

    representation_test("a / (b c)fff")
    representation_test("a / b / c / d")
    representation_test("a")
    representation_test("b (c / d / (e / f))")    
    representation_test("a ((b / f) / (c d)f)")

    def parent_check(element):
        for e in element.elements:
            assert e.parent == element 

    # Some nested alternation wrappings are harder to predict 
    def reptest_advanced(source, expect):
        res = parse_sections(source).represent()
        assert res == expect, res 

    reptest_advanced("a (b / (p f / (d / h)))", "(a (b / ((p f) / (d / h))))")
    reptest_advanced("a (a (b / f) / (c d)f)", "(a ((a (b / f)) / (c d)f))")
    reptest_advanced("a b c / (a (b / b2)z c / d d) c", "((a b c) / (((a (b / b2)z c) / (d d)) c))")
    
    nested_arg_set = parse_sections("f (( ::a)b )c")
    assert len(nested_arg_set.elements) == 2
    a_node = nested_arg_set.elements[1].elements[0].elements[0]
    assert a_node.get_information_array_ordered() == ["::a", "b", "c", ""], \
        "was: " + ",".join([a for a in a_node.get_information_array_ordered()])

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
        UP NEXT: 
        - Proper information detection for each type of element
            - Atomic makes a full parse, section suffix, alternation nothing
    """