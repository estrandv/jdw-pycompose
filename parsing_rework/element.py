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
    
    # Attempt at reconstructing the contents of the element as a parseable string  
    def represent(self, recursion = 0):


        match self.type:
            case ElementType.ATOMIC:
                return self.information
            case ElementType.SECTION:
                return "(" + " ".join([e.represent(recursion + 1) for e in self.elements]) + ")" + self.information \
                    if len(self.elements) > 0 else "ERROR"
            case ElementType.ALTERNATION_SECTION:
                return "(" + " / ".join([e.represent(recursion + 1) for e in self.elements]) + ")" + self.information \
                    if len(self.elements) > 0 else "ERROR"
            case _:
                return "ERROR" 
        
    # Returns an array of information strings, starting with self.information and then resolving parent.informaiton all the way up to the top 
    # Used to retrieve a priority-ordered information set which can then be used for e.g. argument parsing and overwriting. 
    def get_information_array_ordered(self):
        full_information = [] 
        current_node = self
        while current_node != None:
            full_information.append(current_node.information)
            current_node = current_node.parent
        return  full_information      