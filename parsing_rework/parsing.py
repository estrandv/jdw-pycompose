from util import Cursor, Element, ElementType, TreeExpander
import json 

def parse_sections(source_string):
    cursor = Cursor(source_string)
    master_section = Element()
    master_section.type = ElementType.SECTION
    current_element = master_section 

    while True:

        print("CURSOR AT: " + cursor.get())
        
        if cursor.get() == "(":
            current_element = current_element.add()
            current_element.type = ElementType.SECTION
        elif cursor.get() == ")":
            cursor.next()
            if not cursor.is_done():
                current_element.information = cursor.get_until(" ")

            # TODO: Fail safe if element has no parent
            # Convoluted because alternations create nested parents 
            if current_element.parent.type == ElementType.ALTERNATION_SECTION:
                current_element = current_element.parent.parent 
            else:  
                current_element = current_element.parent 
        elif cursor.get() == "/":        

            if current_element.parent != None and current_element.parent.type == ElementType.ALTERNATION_SECTION:
                current_element = current_element.parent.add() 
                current_element.type = ElementType.SECTION
            else:
                # Create an inbetween alternation parent 
                # Nest the ongoing section under it as a new section 
                downport = current_element.elements
                current_element.elements = []
                current_element.type = ElementType.ALTERNATION_SECTION
                nest = current_element.add()
                nest.elements = downport
                nest.type = ElementType.SECTION
                for ele in nest.elements:
                    ele.parent = nest

                # Begin new section after the slash 
                current_element = current_element.add() 
                current_element.type = ElementType.SECTION  
                

            
        elif cursor.get() != " ":
            current_element = current_element.add()
            current_element.type = ElementType.ATOMIC
            current_element.information += cursor.get_until(") ")
            current_element = current_element.parent 

        if cursor.peek() == "":
            break
        else:
            cursor.next()

    


    return master_section 

# ISSUES 
# - Alternation nesting breaks the 22 below 
# - Final element not read due to nature of is_done() check

 

print(parse_sections("abc abc (ala alb / alc (nala nalab)22 )").to_string())

print(parse_sections("a / b / c / d").to_string())

print(parse_sections("outside outside (inside (inside2 (inside3)))bonus / lol").to_string())

print(parse_sections("a b c / (a b c / d d) c").to_string())

# 6  
print(str(parse_sections("b (c / d / (e / f)").alternation_count()))

# Longer alternation test
# EXP: a,b,a,p,f,a,b,a,d,a,b,a,p,f,a,b,a,h
# RES: a,b,a,p,f,a,b,a,d,a,b,a,p,f,a,b,a,h
alt_parse = parse_sections("a (b / (p f / (d / h))")

#print("ALT EXPAND LEN: ", str(len(alt_parse.tree_expand())))

tree = TreeExpander()
print(",".join([e.to_string() for e in tree.tree_expand(alt_parse)]))
