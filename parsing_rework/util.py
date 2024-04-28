from element import ElementType
from cursor import Cursor 
import parsing

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

    def tree_expand(self, element):
        full = []
        #print("Expanding top level: " + element.represent())

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
    def expand(self, element, repeat):

        #print("Expanding section/element: " + element.represent(), element.type)
        #print("Expanding an element with type", element.type, "and information", element.information, "and elements", len(element.elements))

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
# TODO: Naive implementation that does not account for atomics or full informations or whatever 
# TODO: Also no inheritance or reuse or anything. It's basic. 
def get_repeat(element) -> int:
    suffix = parsing.parse_suffix(element.information)
    freetext = parsing.parse_suffix_freetext(suffix.freetext)
    return freetext.repeat

# Returns a flat list containing elements copied N times.
def duplicate(elements, times):
    ret = []
    for _ in range(0, times):
        for e in elements:
            ret.append(e)
    return ret 

# Run tests if ran standalone 
if __name__ == "__main__":

    assert section_split("a b c") == ["a", "b", "c"]
    assert section_split("a (f) c") == ["a", "(f)", "c"]
    assert section_split("a (f (b a ()) / tt) c") == ["a", "(f (b a ()) / tt)", "c"]

    tree = TreeExpander()

    # Quick assertion of atomic elements after a full tree alternations expand    
    # Mixing in some parse logic for faster testing ...     
    def assert_expanded(parse_source, expect):
        top_element = parsing.parse_sections(parse_source)
        tree_expand_string = " ".join([e.information for e in tree.tree_expand(top_element)])
        assert tree_expand_string == expect, tree_expand_string

    assert_expanded("a (b / (p f / (d / h)))", "a b a p f a b a d a b a p f a b a h")

    # Repeat testing
    assert_expanded("x3", "x3 x3 x3")
    assert_expanded("(a b)x2", "a b a b")
    assert_expanded("t / (a / b)", "t a t b")
    assert_expanded("x3 / (a / b)", "x3 x3 x3 a x3 x3 x3 b")    
    assert_expanded("t / (a / b)x3", "t a b a t b a b")
    assert_expanded("t / (f ((a / b)))x2", "t f a f b t f a f b")

    assert_expanded("a (b / c / d)x3", "a b c d")
