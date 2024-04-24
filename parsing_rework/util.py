from enum import Enum



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

    # Returns characters up until, but not including, any of the mentioned symbols
    # Leaves cursor at the found symbol
    def get_until(self, symbols):
        scan = "" 
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
        req_iteratins = element.alternation_count()
        full = []
        for i in range(0, req_iteratins):
            full += element.expand_alternations(self)

        return full

    # Returns the amount of times that this particular element has been ticked so far.
    # Used to keep track of which alternation to return. 
    def tick(self,element):
        count = len([e for e in self.tick_list if e is element])
        self.tick_list.append(element)
        return count 

class ElementType(Enum):
    SECTION = 0
    ALTERNATION_SECTION = 1
    ATOMIC = 2

class Element:
    def __init__(self):
        self.elements = []
        self.information = ""
        self.type = ElementType.ATOMIC
        self.parent = None

    def add(self):
        self.elements.append(Element())
        self.elements[-1].parent = self 
        return self.elements[-1]

    # TODO: Place in the tree instead
    def expand_alternations(self, tree):
        if self.type == ElementType.ATOMIC:
            return [self]
        if self.type == ElementType.SECTION:
            flatmap = []
            matrix = [e.expand_alternations(tree) for e in self.elements]
            for c in matrix:
                for r in c:
                    flatmap.append(r)
            return flatmap
        if self.type == ElementType.ALTERNATION_SECTION:
            
            ticks = tree.tick(self)
            mod = ticks % (len(self.elements))
            current_alt = self.elements[mod]
            return current_alt.expand_alternations(tree)
        return []

    # TODO: Consider placing in tree as well
    def alternation_count(self):

        base = 1
        
        if self.type == ElementType.ALTERNATION_SECTION:
            base = len(self.elements)

        return base * max([ele.alternation_count() for ele in self.elements] + [1])
    
    def to_string(self):
        if self.type == ElementType.ATOMIC:
            return self.information
        else:
            nested = [ele.to_string() for ele in self.elements]

            sym = " /" if self.type == ElementType.ALTERNATION_SECTION else ","
            brackets = ["[", "]"] if self.type == ElementType.ALTERNATION_SECTION else ["(", ")"]
            
            contents = brackets[0] + (sym + " ").join(nested) + brackets[1]
            
            #if self.type == ElementType.ALTERNATION_SECTION:
            #    contents = "*" + contents + "*"
            
            if self.type == ElementType.ALTERNATION_SECTION:
                contents = contents 
            if self.information != "":
                contents += self.information 
            return contents
        
    # Returns an array of information strings, starting with self.information and then resolving parent.informaiton all the way up to the top 
    # Used to retrieve a priority-ordered information set which can then be used for e.g. argument parsing and overwriting. 
    def get_information_array_ordered(self):
        full_information = [] 
        current_node = self
        while current_node != None:
            full_information.append(current_node.information)
            current_node = current_node.parent
        return  full_information      