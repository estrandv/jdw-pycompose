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
#   -> We can survive without this for a while; won't affect anything else 
# - Consider a new arg symbol: a3name_sus0.2 g5@name=0.2,amp0.5
#   -> Not terribly important yet; ":" works 
# - "Argument" is not at all what it is and it should be renamed
#   -> Easier to do once all the old code is gone 
# - Make POC for actual synth sending 
#   -> First, make a proper library as a separate repo and pip install it 

# - Add "_" or "." as a valid standin for index (perhaps it lready works?)
empty = parser.parse(". . .")
print(empty[0].suffix) # Dead symbol always suffix, 0-default for index