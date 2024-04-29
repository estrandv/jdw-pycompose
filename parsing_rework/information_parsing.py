"""

    Parsing related to single-element string-parts. 

"""

from enum import Enum
from cursor import Cursor
from dataclasses import dataclass
from decimal import Decimal
from element import Element, ElementType
import pytest 

"""
    TODO: Discussion on requirements. 
    - Can index be a float?
    - When do we need symbols -instead- of an index? 
    - How do we denote e.g. "mod note number of playing note"? Suffix? Symbol?
        -> Ideally we always have a number, with suffix containing an extra symbol  
    - Should it even be possible to have a suffix without an index? If so, how? 
        -> Possible for section, of course, but not atomic 

"""
@dataclass
class ElementInformation:
    prefix: str = "" # Contents prior to first numeric or special symbol 
    index_string: str = "" # First numeric or special symbol
    suffix: str = "" # Contents after first numeric or special symbol
    repetition: int = 1 # Contents after "*", but before ":"
    arg_source: str = "" # Final contents, after ":"

class InformationPart(Enum):
    PREFIX = 0
    INDEX = 1
    SUFFIX = 2
    REPETITION = 3
    ARGS = 4

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
                    current_part = InformationPart.SUFFIX
                    # NOTE: Implicit straight-to-suffix on no number
                    # Below is the error we used to throw: 
                    #raise Exception("Malformed input - element information has no index: " + element.information)
                else:
                
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

                remaining = cursor.get_remaining() 

                star_index = remaining.find("*")
                colon_index = remaining.find(":")

                # Since * can appear inside args, we need to check for it before arg declaration 
                star_present = star_index != -1 and (star_index < colon_index or colon_index == -1) 

                if star_present:
                    information.suffix = cursor.get_until("*")
                    cursor.move_past_next("*")
                    current_part = InformationPart.REPETITION
                elif ":" in remaining:
                    information.suffix = cursor.get_until(":")
                    cursor.move_past_next(":")
                    current_part = InformationPart.ARGS
                else:
                    information.suffix = remaining
                    break 

            case InformationPart.REPETITION:
                remaining = cursor.get_remaining() 
                if ":" in remaining:
                    information.repetition = int(cursor.get_until(":"))
                    cursor.move_past_next(":")
                elif remaining != "":
                    information.repetition = int(remaining)

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
class DynamicArg:
    value: Decimal
    operator: str = ""

# Parse 1.0,arg+2,argb*2.0,argc0.2 [...] part of element info suffix 
def parse_args(arg_source) -> dict:
    args = {}

    cursor = Cursor(arg_source)
    while True: 
        # Step on separator at a time 
        content = cursor.get_until(",")

        sub_cursor = Cursor(content)
        # Numbers or operators break the key part
        # TODO: Consider ".2" shorthand support 
        non_numeric = sub_cursor.get_until("0123456789+-*")

        # Step into the numeric part of the string unless it began immediately 
        if sub_cursor.peek() != "" and non_numeric != "":
            sub_cursor.next()

        numeric = sub_cursor.get_remaining()

        if numeric != "": 

            num = "".join(numeric[1:]) if numeric[0] in "+-*" else numeric
            sym = numeric[0] if numeric[0] in "+-*" else ""    

            numeric_decimal = Decimal(num)

            new_arg = DynamicArg(numeric_decimal, sym)

            if non_numeric == "":
                if len(args) == 0:
                    # TODO: Some other way to provide this default 
                    # First arg is "time" unless otherwise noted 
                    args["time"] = new_arg
                else:
                    raise Exception("Malformed input: unnamed non-first arg")
            else:
                args[non_numeric] = new_arg

        cursor.move_past_next(",")
        if cursor.is_done():
            break 

    return args 

# Run tests if ran standalone 
if __name__ == "__main__": 

    # Args tests 

    no_arg_test = parse_args("")
    assert len(no_arg_test) == 0

    arg_test_basic = parse_args("1.0")
    assert arg_test_basic["time"].value == Decimal("1.0"), arg_test_basic["time"].value
    assert len(arg_test_basic) == 1, len(arg_test_basic)

    arg_test_basic_2 = parse_args("fish1.0,cheese0.3")
    assert "fish" in arg_test_basic_2
    assert "cheese" in arg_test_basic_2
    assert arg_test_basic_2["fish"].value == Decimal("1.0"), arg_test_basic_2["fish"].value
    assert arg_test_basic_2["cheese"].value == Decimal("0.3"), arg_test_basic_2["cheese"].value
    
    arg_test = parse_args("0.2,;900,lob0.002")
    assert "time" in arg_test
    assert ";" in arg_test
    assert "lob" in arg_test
    assert arg_test["time"].value == Decimal("0.2"), arg_test["time"].value
    assert arg_test[";"].value == Decimal("900"), arg_test[";"].value
    assert arg_test["lob"].value == Decimal("0.002"), arg_test["lob"].value

    symtest = parse_args("a+4,b*0.2,c-1.2,d0.3")
    assert symtest["a"].operator == "+", symtest["a"].operator
    assert symtest["b"].operator == "*", symtest["b"].operator
    assert symtest["c"].operator == "-", symtest["c"].operator
    assert symtest["d"].operator == "", symtest["d"].operator


    # Divide information testing

    def make_element(source, etype):
        ele = Element() 
        ele.information = source
        ele.type = etype
        return ele 

    def divide_test(source, prefix, index, suffix, repeat, args):
        divtest = divide_information(make_element(source, ElementType.ATOMIC))
        assert divtest.prefix == prefix, divtest.prefix
        assert divtest.index_string == index, divtest.index_string
        assert divtest.suffix == suffix, divtest.suffix
        assert divtest.repetition == repeat, divtest.repetition
        assert divtest.arg_source == args, divtest.arg_source

    divide_test("a3x:0.1@", "a", "3", "x", 1, "0.1@")
    divide_test("1", "", "1", "", 1, "")
    divide_test("9099:arg1", "", "9099", "", 1, "arg1")
    divide_test("001xxx", "", "001", "xxx", 1, "")
    divide_test("", "", "", "", 1, "")
    divide_test("a", "", "", "a", 1, "")
    divide_test("prefix33suf*3:arg0.1,arf0.2", "prefix", "33", "suf", 3, "arg0.1,arf0.2")

    stest = divide_information(make_element(":fff", ElementType.SECTION))
    assert stest.prefix == ""
    assert stest.index_string == ""
    assert stest.suffix == ""
    assert stest.arg_source == "fff" 

    startest = divide_information(make_element(":ss*s", ElementType.SECTION))
    assert stest.suffix == ""

    with pytest.raises(Exception) as exc_info:   
        divide_information(make_element(":fff", ElementType.ATOMIC))
        assert "Malformed input" in exc_info.value
