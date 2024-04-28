"""

    Parsing related to single-element string-parts. 

"""

from enum import Enum
from cursor import Cursor
from dataclasses import dataclass
from decimal import Decimal
from element import Element, ElementType

"""
    TODO: Discussion on requirements. 
    - Can index be a float?
    - When do we need symbols -instead- of an index? 
    - How do we denote e.g. "mod note number of playing note"? Suffix? Symbol?  
    - Should it even be possible to have a suffix without an index? If so, how? 

"""
@dataclass
class ElementInformation:
    prefix: str = "" # Contents prior to first numeric or special symbol 
    index_string: str = "" # First numeric or special symbol
    suffix: str = "" # Contents after first numeric or special symbol
    arg_source: str = "" # Final contents, after ":"

class InformationPart(Enum):
    PREFIX = 0
    INDEX = 1
    SUFFIX = 2
    ARGS = 3

def divide_information(element: Element) -> ElementInformation:

    # Initiate with blank defaults 
    information = ElementInformation() 

    # Sections start at suffix; they have no prefix or index 
    current_part = InformationPart.SUFFIX \
        if element.type in [ElementType.SECTION, ElementType.ALTERNATION_SECTION] \
        else InformationPart.PREFIX

    # Return blank when no information string is provided 
    if element.information == "":
        return information

    cursor = Cursor(element.information)

    NUMBERS = "0123456789"

    while True:
        match current_part:
            case InformationPart.PREFIX:
                if not cursor.contains_any(NUMBERS):
                    raise Exception("Malformed input - element information has no index: " + element.information)
                until_number = cursor.get_until(NUMBERS)
                information.prefix = until_number

                # NOTE: Cursor weakness - if first character matches get_until we don't stop "before it" 
                if cursor.get() not in NUMBERS:
                    cursor.next()

                current_part = InformationPart.INDEX

            case InformationPart.INDEX:
                information.index_string = cursor.get_until("0123456789", False)
                
                # NOTE: Again, cursor weakness
                if cursor.get() in NUMBERS:
                    cursor.next()

                current_part = InformationPart.SUFFIX
            
            case InformationPart.SUFFIX:
                
                if not cursor.is_done():
                    information.suffix = cursor.get_until(":")
                    cursor.move_past_next(":")

                current_part = InformationPart.ARGS

            case InformationPart.ARGS:

                if not cursor.is_done():
                    information.arg_source = cursor.get_remaining()

                break 

            case _:
                # Shouldn't happen but w/e
                break

    return information



@dataclass
class SuffixInfo:
    freetext: str = ""
    arg_source: str = ""

# TODO: Replace with full blown information data class that is 
#   parsed based on element type 
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

# Run tests if ran standalone 
if __name__ == "__main__": 

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

    # Divide information testing

    def make_element(source):
        ele = Element() 
        ele.information = source 
        return ele 

    divtest = divide_information(make_element("a3x:0.1@"))
    assert divtest.prefix == "a", divtest.prefix
    assert divtest.index_string == "3", divtest.index_string
    assert divtest.suffix == "x", divtest.suffix
    assert divtest.arg_source == "0.1@", divtest.arg_source
