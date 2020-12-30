from __future__ import annotations # Not needed after python 3.10

# 0:C 1:C# 2:D 3:D# 4:E 5:F 6:F# 7:G 8:G# 9:A 10:A# 11:B


CHROMATIC=[0,1,2,3,4,5,6,7,8,9,11]
MAJOR=[0,2,4,5,7,9,11] # TODO: Next tone is 12, but our math would resolve it to 11 again. It's next octave.
MAJOR_PENTATONIC=[0,2,4,7,9]
MINOR=[0,2,3,5,7,8,10]
MINOR_PENTATONIC=[0,3,5,7,10]
EGYPTIAN=[0,2,5,7,10]
HUNGARIAN_MINOR=[0,2,3,6,7,8,11]

# TODO: Trying to wrap my head around this.
# THe tricky part is that we need to loop around both scales and octaves
# While at the same time continuing the scales in a custom fashion
# [0,2,4] has three tones, what should the fourth be? If it's index+value it's 4, but that's wrong.
# It should be 12; the start of the next octave. It diesn't loop around, it applies itself on
# the next octave. 

# SO THE FORMULA IS?
# a. Find where in the octave the tone is, e.g. c4 would be 0
# b. Save which octave you're in
# c. Find out if the scale value for the octave tone, e.g. 0 in major would be 0
# d. If the octave tone is greater than the scale, we get a "bonus octave" by the number
# e. End result is scale[octave_tone] 
def transpose(tone_index: int, scale: List[int]) -> int:

    # A MIDI Octave is 12 notes, starting with note 0 and ending with 11.
    octave_len = len(CHROMATIC) + 1
    print("OCtave length: " + str(octave_len))

    print("Tone: " + str(tone_index))

    scale_indices = len(scale)
    print("Scale len: " + str(scale_indices))

    # By splitting tone index by octave length (and rounding down),
    # we establish in which octave the tone resides.
    octave_index = int( tone_index / (octave_len) )

    # Once we know the octave, we want to know where in the octave the tone is
    # E.g. tone_index 23 is octave_index 1 with 23-(1*12)=11 as tone index in octave
    tone_index_in_octave = tone_index - (octave_index * (octave_len))
    print("Octave Index: " + str(octave_index))
    print("Position in octave: " + str(tone_index_in_octave))

    # The amount of times (rounded down) that the tone rounds the available indices in the array
    # Given an array with max index 4 and a tone of 11, the overshoot would be 2
    # We want to basically loop around the scale to find an available index that matches the 
    # tone index in octave.
    # If index is 4 and the scale has a max index of 3, we get 1 overshoot
    #   In that case, remainder would calculate as 4 - (1 * 3) = 1
    overshoot = int(tone_index_in_octave / scale_indices)
    print("Scale Overshoot: " + str(overshoot))
    remainder = tone_index_in_octave - (overshoot * scale_indices)
    print("Selected Scale Index: " + str(remainder))

    # By now we know the position in the octave and how to divide that to get the 
    #   position in the scale. We can then add that value to the original tone plus
    #   any bonus octaves from overshoot.
    final = scale[remainder] + tone_index + ((overshoot) * octave_len)

    print("Scale value: " + str(scale[remainder]))

    print("final (in octave): " + str(final))
    print("----------------")

    # Return the scale determined tone value in the octave determined by overshoot
    return final

# Test to verify tones as expected for major scale
def test():

    # The tones are as decoded from parsing lib, starting at A
    # A should be the first note in the third or fourth octave
    # But my scale lib says it should be the third in the third (fourth, technically)
    # OCTAVES:
    # 1: starts at 0, ends at 11
    # 2: starts at 12, ends at 23
    # 3: starts at 24, ends at 35
    # 4: starts at 36
    # Thus my scale lib is lying about octave position.

    tones = [36,37,38,39, 40,41,42, 43]
    scale=[0,2,4,5,7,9,11]
    expected = [36,39,42,44, 47,50,53, 55]
    
    i = 0
    for tone in tones:
        result = transpose(tone, scale)
        if result != expected[i]:
            print("### ERROR: Tone " + str(tone) + " should become " + str(expected[i]) + ", not " + str(result))
            print("----------------------")
       
        i += 1