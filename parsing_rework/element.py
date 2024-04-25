from enum import Enum

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

    # TODO: Consider placing in tree instead 
    def alternation_count(self):

        base = 1
        
        if self.type == ElementType.ALTERNATION_SECTION:
            base = len(self.elements)

        # Max of [AC, 1]
        return base * max([ele.alternation_count() for ele in self.elements] + [1])
    
    # TODO: Used for quick, brainless print tests. Highly unstable, don't use for asserts... 
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