import information_parsing
import section_parsing
import element
import util
import element_resolving

def parse(source_string: str) -> list[element.ResolvedElement]:
    # Run the whole intended sequence of parsing, from source to final elements 
    top_element = section_parsing.build_tree(source_string)
    tree = util.TreeExpander() 
    sequence = tree.tree_expand(top_element)
    return [element_resolving.resolve(e) for e in sequence]