from element import ElementType
import parsing

# Used for step-parsing strings

class Cursor: 
    def __init__(self, source_string):
        self.source_string = source_string
        self.cursor_index = 0

    def is_done(self):
        return self.cursor_index > len(self.source_string) - 1

    def next(self):
        self.cursor_index += 1

    def peek(self):
        index = self.cursor_index + 1 
        if index <= len(self.source_string) - 1:
            return self.source_string[index]
        else:
            return "" 

    def get(self):
        return self.source_string[self.cursor_index]

    def get_remaining(self):
        return "".join(self.source_string[self.cursor_index:])

    # Place cursor on index after next occurrence of any of the mentioned symbols
    def move_past_next(self, symbols):

        while True: 
            if self.is_done():
                break 
            else:
                current = self.get()
                self.next()
                if current in symbols:
                    break 
        return  

    # Returns characters up until, but not including, any of the mentioned symbols
    # Leaves cursor before the found symbol
    def get_until(self, symbols):
        scan = ""

        if self.is_done():
            return ""

        while True:

            
            current = self.get()
            ahead = self.peek() 

            if current in symbols:
                break 
            else: 
                scan += current
                if ahead in symbols or ahead == "":
                    break 
                self.next() 

        return scan

class TreeExpander:

    def __init__(self):
        self.tick_list = []
    
    def tree_expand(self, element):
        # Count how many times one would have to iterate the whole set to expand all nested alternations 
        req_iteratins = element.alternation_count()
        full = []
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

    """ 
    assert_expanded("t / (a / b)x3", "t a b a t b a b")