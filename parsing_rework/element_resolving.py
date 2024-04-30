from element import Element, ElementType, ResolvedElement
import information_parsing
import util 

def resolve(element: Element) -> ResolvedElement:
    
    match element.type:
        case ElementType.ATOMIC:
            info = information_parsing.divide_information(element)
            history = util.get_information_history(element)
            args = util.resolve_full_arguments(history)
            resolved = ResolvedElement(info.prefix, int(info.index_string), info.suffix, args)
            return resolved 

        case _:
            raise Exception("Only ATOMIC elements can be resolved!")
