from element import ElementType
from cursor import Cursor 
import section_parsing
import information_parsing
from decimal import Decimal

# "Business logic" - explain later 
def section_split(source_string) -> list:
    cursor = Cursor(source_string)

    opened_parentheses = 0

    everything = []

    current = ""

    while not cursor.is_done(): 
        match cursor.get():
            case "(": 
                current += cursor.get() 
                opened_parentheses += 1
            case ")":
                current += cursor.get() 
                opened_parentheses -= 1
            case " ":
                if opened_parentheses == 0:
                    if current != "":
                        everything.append(current)
                    current = ""
                else:
                    current += cursor.get()
            case _:
                current += cursor.get()
        cursor.next() 

    if current != "":
        everything.append(current)

    return everything 

class TreeExpander:

    def __init__(self):
        self.tick_list = []

    # Count how many times one would have to use the element to fully expand it and its children. 
    def count_required_alternations(self, element):

        base = 1
        
        if element.type == ElementType.ALTERNATION_SECTION:
            base = len(element.elements)

        # Max of [AC, 1]
        return base * max([self.count_required_alternations(ele) for ele in element.elements] + [1])

    def all_ticked(self, element) -> bool:
        element_ticks = self.get_ticks(element)

        required_ticks = self.count_required_alternations(element) \
            if element.type == ElementType.ALTERNATION_SECTION \
            else 1
        
        children_ok = True 
        for child in element.elements:
            if not self.all_ticked(child):
                children_ok = False

        #print("Ticked", element_ticks, "required", required_ticks)
        
        return element_ticks >= required_ticks and children_ok

    def tree_expand(self, element) -> list:
        full = []

        while not self.all_ticked(element):
            full += self.expand(element, get_repeat(element))

        return full

    # Tick off an element, so that we can count how many times we have done so. 
    # Alternations must be used several times to fully expand, hence the need to count. 
    def tick(self,element):
        self.tick_list.append(element)

    # Returns how many times an element has been ticked so far.
    # Does not account for children.  
    def get_ticks(self, element):
        return len([e for e in self.tick_list if e is element])

    # Expand both alternations and repeats 
    def expand(self, element, repeat) -> list:

        if element.type == ElementType.ATOMIC:
            self.tick(element)
            return duplicate([element], repeat) 
        if element.type == ElementType.SECTION:
            flatmap = []
            for _ in range(0, repeat):
                self.tick(element)
                matrix = [self.expand(e, get_repeat(e)) for e in element.elements]
                for c in matrix:
                    for r in c:
                        flatmap.append(r)
            return flatmap 
        if element.type == ElementType.ALTERNATION_SECTION:

            # Repeat the alternation as required, grabbing the next alternation each time
            full = [] 
            for i in range(0, repeat):
                # Tick element and return amount of times it has been ticked            
                ticks = self.get_ticks(element)
                self.tick(element)
                # Resolve an index from the tick amount (so that, in a 2-len array, 2 follows after 1, 0 after 2, etc)
                mod = ticks % (len(element.elements))
                current_alt = element.elements[mod]
                full += self.expand(current_alt, get_repeat(current_alt))
            return full 

        return []

# Returns the amount of times an element should be repeated, according to its "xN" suffix
def get_repeat(element) -> int:
    information = information_parsing.divide_information(element)
    return information.repetition

# Returns a flat list containing elements copied N times.
def duplicate(elements, times):
    ret = []
    for _ in range(0, times):
        for e in elements:
            ret.append(e)
    return ret 

# Get the information of the element and all its parents, in that order
def get_information_history(element) -> list:
    full_list = []
    current_element = element
    while current_element != None:
        info = information_parsing.divide_information(current_element)
        full_list.append(info)
        current_element = current_element.parent

    return full_list

# Resolve arguments from the top down of the given element information history. 
# The topmost definition is used as base - args with operations 
#   override the base, args without replace it. 
def resolve_full_arguments(information_history: list) -> dict:

    # Walk to the top parent, collecting all argument dicts along the way. 
    all_arg_dicts = []

    for info in information_history:
        if info.arg_source != "":
            args = information_parsing.parse_args(info.arg_source)
            all_arg_dicts.append(args)
        
    # Reverse priority order; begin with topmost args. 
    all_arg_dicts.reverse()

    # Non-dynamic args; dict of <str,Decimal>
    resolved_args = {}

    for arg_dict in all_arg_dicts:
        for dynamic_arg_key in arg_dict:
            dynamic_arg = arg_dict[dynamic_arg_key]
            # Arg present at a higher level and can be modified 
            if dynamic_arg_key in resolved_args:
                match dynamic_arg.operator:
                    case "*":
                        resolved_args[dynamic_arg_key] *= dynamic_arg.value
                    case "+":
                        resolved_args[dynamic_arg_key] += dynamic_arg.value
                    case "-":
                        resolved_args[dynamic_arg_key] *= dynamic_arg.value
                    case _:
                        # Blank or unknown operator should overwrite
                        resolved_args[dynamic_arg_key] = dynamic_arg.value
            else:
                # Introduce without any operators if no higher level version exists
                resolved_args[dynamic_arg_key] = dynamic_arg.value

    return resolved_args

# Run tests if ran standalone 
if __name__ == "__main__":

    assert section_split("a b c") == ["a", "b", "c"]
    assert section_split("a (f) c") == ["a", "(f)", "c"]
    assert section_split("a (f (b a ()) / tt) c") == ["a", "(f (b a ()) / tt)", "c"]

    tree = TreeExpander()

    # Quick assertion of atomic elements after a full tree alternations expand    
    # Mixing in some parse logic for faster testing ...     
    def assert_expanded(parse_source, expect):
        top_element = section_parsing.build_tree(parse_source)
        tree_expand_string = " ".join([e.information for e in tree.tree_expand(top_element)])
        assert tree_expand_string == expect, tree_expand_string

    assert_expanded("1 (2 / (3 4 / (5 / 6)))", "1 2 1 3 4 1 2 1 5 1 2 1 3 4 1 2 1 6")

    # Repeat testing
    assert_expanded("2*3", "2*3 2*3 2*3")
    assert_expanded("(1 2)*2", "1 2 1 2")
    assert_expanded("t / (a / b)", "t a t b")
    assert_expanded("2*3 / (a / b)", "2*3 2*3 2*3 a 2*3 2*3 2*3 b")    
    assert_expanded("t / (a / b)*3", "t a b a t b a b")
    assert_expanded("t / (f ((a / b)))*2", "t f a f b t f a f b")

    assert_expanded("a (b / c / d)*3", "a b c d")

    # Arg resolution testing

    ### Verify history logic 
    grandparent = section_parsing.build_tree("((0a)b)c")
    child = grandparent.elements[0].elements[0].elements[0]
    h1 = [i.suffix for i in get_information_history(child)]
    assert h1 == ["a", "b", "c", ""], h1

    # Fake an information history using bastardized parsing 
    def build_arg_array(source):
        elements = section_parsing.build_tree(source).elements
        return [information_parsing.divide_information(e) for e in elements]

    def arg_tree_test(array_source, expected_dict):
        history = build_arg_array(array_source)
        args = resolve_full_arguments(history)

        for key in expected_dict:
            assert args[key] == expected_dict[key], args[key]

    arg_tree_test("a3:aa0.2,ab+0.2,ac-0.2", {
        "aa": Decimal("0.2"),
        "ab": Decimal("0.2"),
        "ac": Decimal("0.2")
    })

    arg_tree_test("0:a+0.1 0:a+0.1 0:a+0.1", {
            "a": Decimal("0.3")
    })
        
    arg_tree_test("0:a+0.1 0:a*0.5 0:a2.0", {
            "a": Decimal("1.1")
    })
    
    arg_tree_test("0:a0.2 0:a*44 0:a1", {
            "a": Decimal("0.2")
    })
    


