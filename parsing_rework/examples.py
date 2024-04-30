# Workshop file, used for manual testing and planning
from full_parse import parse

# Run the whole intended sequence of parsing, from source to final elements 
resolved = parse("a3*3:2.0 (d3 / g3:*0.5 / d3 / c4):0.5")
print(" ".join([e.to_str() for e in resolved]))