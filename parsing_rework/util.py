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
    
    def tree_expand(self, element):
        # Count how many times one would have to iterate the whole set to expand all nested alternations 
        req_iteratins = element.alternation_count()
        full = []
        print("Expanding top level: " + element.represent())
        for i in range(0, req_iteratins):
            full += self.expand(element, get_repeat(element))

        return full

    # Returns the amount of times that this particular element has been ticked so far.
    # Used to keep track of which alternation to return. 
    def tick(self,element):
        count = len([e for e in self.tick_list if e is element])
        self.tick_list.append(element)
        return count 

    # Expand both alternations and repeats 
    def expand(self, element, repeat):

        print("Expanding section/element: " + element.represent(), element.type)
        #print("Expanding an element with type", element.type, "and information", element.information, "and elements", len(element.elements))

        if element.type == ElementType.ATOMIC:
            return duplicate([element], repeat) 
        if element.type == ElementType.SECTION:
            flatmap = []
            matrix = [self.expand(e, get_repeat(e)) for e in element.elements]
            for c in matrix:
                for r in c:
                    flatmap.append(r)
            return duplicate(flatmap, repeat) 
        if element.type == ElementType.ALTERNATION_SECTION:

            # Repeat the alternation as required, grabbing the next alternation each time
            full = [] 
            for i in range(0, repeat):
                # Tick element and return amount of times it has been ticked            
                ticks = self.tick(element)
                # Resolve an index from the tick amount (so that, in a 2-len array, 2 follows after 1, 0 after 2, etc)
                mod = ticks % (len(element.elements))
                current_alt = element.elements[mod]
                full += self.expand(current_alt, get_repeat(current_alt))
            return full 

        return []

# TODO: Naive implementation that does not account for atomics or full informations or whatever 
# TODO: Also no inheritance or reuse or anything. It's basic. 
def get_repeat(element) -> int:
    suffix = parsing.parse_suffix(element.information)
    freetext = parsing.parse_suffix_freetext(suffix.freetext)
    return freetext.repeat

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

    #assert_expanded("a (b / (p f / (d / h))", "a b a p f a b a d a b a p f a b a h")

    # Repeat testing
    #assert_expanded("x3", "x3 x3 x3")
    #assert_expanded("(a b)x2", "a b a b")
    #assert_expanded("t / (a / b)", "t a t b")
    #assert_expanded("x3 / (a / b)", "x3 x3 x3 a x3 x3 x3 b")
    # TODO: Other tests commented for better debug - something isn't detecting repeats properly 
    # Likely due to repeats being part of some hidden, nested section
    """
        - Top level should count as an alternation section with no information
        - The second level becomes a regular section (a / b)x3
        - a / b is then an alternation with no repeat argument
            - But its parent should have it 
            - Although, as noted for top level, there isn't always a parent  
            - Either way, alternations will always be nested and thus never have _information_ 
                -> See tests in parsing for what types to expect

        - Evening note: I feel like there's something wrong in the logic. If 
            top level can be alternation without section nesting, ()-parts should
            be able to as well. Might be I misunderstand.  

    """ 
    assert_expanded("t / (a / b)x3", "t a b a t b a b")