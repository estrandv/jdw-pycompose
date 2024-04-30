# Workshop file, used for manual testing and planning
from full_parse import Parser

# Run the whole intended sequence of parsing, from source to final elements 
parser = Parser() 
resolved = parser.parse("a3*3:2.0 (d3 / g3:*0.5 / d3 / c4):0.5")
print(" ".join([e.to_str() for e in resolved]))

parser.arg_aliases = {">": "sus", "!": "amp"}
resolved = parser.parse("999:>0.2,!1.0 999:0.0,>1.0,!0.5")
print(" ".join([e.to_str() for e in resolved]))

# TODO: Next up 
# - Add arg symbol for implied top level section 