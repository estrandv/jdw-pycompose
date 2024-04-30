from enum import Enum
from dataclasses import dataclass

class ElementType(Enum):
    SECTION = 0
    ALTERNATION_SECTION = 1
    ATOMIC = 2

# Atomic element after all parsing complete
@dataclass
class ResolvedElement:
    prefix: str
    index: int
    suffix: str
    args: dict     

    def to_str(self) -> str:
        arg_str = "" if len(self.args) == 0 else ":"
        arg_str += ",".join([key + str(self.args[key]) for key in self.args])
        return self.prefix + str(self.index) + self.suffix + arg_str

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

    # Attempt at reconstructing the contents of the element as a parseable string. 
    # Writes the string as interpreted, not as originally written, and will thus have
    #   implied sections written out explicitly.
    def decompile(self, recursion = 0):
        match self.type:
            case ElementType.ATOMIC:
                return self.information 
            case ElementType.SECTION:
                return "(" + " ".join([e.decompile(recursion + 1) for e in self.elements]) + ")" + self.information \
                    if len(self.elements) > 0 else "ERROR"
            case ElementType.ALTERNATION_SECTION:
                return "(" + " / ".join([e.decompile(recursion + 1) for e in self.elements]) + ")" + self.information \
                    if len(self.elements) > 0 else "ERROR"
            case _:
                return "ERROR" 



    # Returns an array of information strings, starting with self.information and then resolving parent.informaiton all the way up to the top 
    # Used to retrieve a priority-ordered information set which can then be used for e.g. argument parsing and overwriting. 
    # TODO: Fetch information objects instead, or even args directly if that's all that matters 
    def get_information_array_ordered(self):
        full_information = [] 
        current_node = self
        while current_node != None:
            full_information.append(current_node.information)
            current_node = current_node.parent
        return  full_information      