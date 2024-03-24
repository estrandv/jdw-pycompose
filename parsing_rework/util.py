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

    
    def tree_expand(self):
        req_iterations = self.alternation_count() 
        full = []
        for i in range(0, req_iterations - 1):
            full += self.expand_alternations(i)
        return full

    def expand_alternations(self, iteration: int):
        if self.type == ElementType.ATOMIC:
            return [self]
        if self.type == ElementType.SECTION:
            flatmap = []
            matrix = [e.expand_alternations(iteration) for e in self.elements]
            for c in matrix:
                for r in c:
                    flatmap.append(r)
            return flatmap
        if self.type == ElementType.ALTERNATION_SECTION:
            mod = iteration % (len(self.elements))
            current_alt = self.elements[mod]
            print("EXPANDING: ", current_alt.to_string(), str(mod), str(len(self.elements)), str(iteration))            
            return current_alt.expand_alternations(iteration)
        return []

    def alternation_count(self):

        base = 1
        
        if self.type == ElementType.ALTERNATION_SECTION:
            base = len(self.elements)
            print("BASE TO " + str(base))

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
        
