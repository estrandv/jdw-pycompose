# Intro 

This is an instruction prompt. Inquiries will follow after. For now, just study these instructions. 

Consider a notation language for music with the following spec (let's call the language JDW-SCRIPT or JDW):

# Notes 
Notes can be represented as space-separated numerical symbols ("numeric format JDW"), which determine which note is played in a given scale (decided elsewhere).

Example: 0 1 2 3 0 2 1 3

Notes can also be specified as absolute notes ("letter format JDW"), where, for example, "g in octave 4" would be "g4". 

Example: c4 d4 g4 d3

Notes are only ever space-separated - don't include newlines in output. 

Notes are raised with 

# Properties

Properties of each note are specified before the separating space, but after the ":" symbol. 

Properties are typically specified as "name0.8", where the decimal number sets the value. 

This allows us to set things like the reserved time of the note in beats, the sustain time in beats, and many other things.

If a number immediately follows the ":", the language defaults to assigning that value as "reserved time" since it is the most common property. Reserved time in JDW is equivalent to the amount of beats a note "lasts" in common musical notation. 0.25 is a quarter, 0.125 is an eighth, and so on.  

Example (a 4-beat melody): 0:1.5 2:0.5,sus0.5 0:1,sus2.3 3:1

# Snippet Generation 

Unless otherwise specified, I'm typically only interested in generating JDW snippets with the time property specified - I don't usually need any other properties (like sustain) filled in. 

If I ask for a snippet to be generated, please follow the following formula: 
1. Determine the original music notation or midi spec for the song, if it is a known melody. Use internet midi or music sheet databases for sourcing if the melody is not already present in your internal data.  
2. Translate the original notation into JDW. For each note: 
    a. Assign the correct number (assuming a scale) or letter/octave, depending on format. 
    b. Assign the correct reserved time based on the note length in the original notation. Always preserve the original rhythm.  
3. If you are unable to find any source material, don't make things up. Instead ask if I would want you to generate something original. 
4. Keep the answer brief and focus on the generated snippet