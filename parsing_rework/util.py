from element import ElementType

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
            full += self.expand_alternations(element)

        return full

    # Returns the amount of times that this particular element has been ticked so far.
    # Used to keep track of which alternation to return. 
    def tick(self,element):
        count = len([e for e in self.tick_list if e is element])
        self.tick_list.append(element)
        return count 

    def expand_alternations(self, element):
        if element.type == ElementType.ATOMIC:
            return [element]
        if element.type == ElementType.SECTION:
            flatmap = []
            matrix = [self.expand_alternations(e) for e in element.elements]
            for c in matrix:
                for r in c:
                    flatmap.append(r)
            return flatmap
        if element.type == ElementType.ALTERNATION_SECTION:

            # Tick element and return amount of times it has been ticked            
            ticks = self.tick(element)
            # Resolve an index from the tick amount (so that, in a 2-len array, 2 follows after 1, 0 after 2, etc)
            mod = ticks % (len(element.elements))
            current_alt = element.elements[mod]
            return self.expand_alternations(current_alt)
        return []
