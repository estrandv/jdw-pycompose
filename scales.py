from __future__ import annotations # Not needed after python 3.10

# 0:C 1:C# 2:D 3:D# 4:E 5:F 6:F# 7:G 8:G# 9:A 10:A# 11:B

CHROMATIC=[0,1,2,3,4,5,6,7,8,9,11]
MAJOR=[0,2,4,5,7,9,11]
MAJOR_PENTATONIC=[0,2,4,7,9]
MINOR=[0,2,3,5,7,8,10]
MINOR_PENTATONIC=[0,3,5,7,10]
EGYPTIAN=[0,2,5,7,10]
HUNGARIAN_MINOR=[0,2,3,6,7,8,11]

def transpose(tone_index: int, scale: list[int]) -> int:

    # A MIDI Octave is 12 notes, starting with note 0 and ending with 11.
    octave_len = len(CHROMATIC) + 1

    scale_indices = len(scale)

    # By splitting tone index by octave length (and rounding down),
    # we establish in which octave the tone resides.
    octave_index = int( tone_index / (octave_len) )

    # Once we know the octave, we want to know where in the octave the tone is
    # E.g. tone_index 23 is octave_index 1 with 23-(1*12)=11 as tone index in octave
    tone_index_in_octave = tone_index - (octave_index * (octave_len))

    # The amount of times (rounded down) that the tone rounds the available indices in the array
    # We want to basically loop around the scale to find an available index that matches the 
    # tone index in octave.
    # If index is 4 and the scale has a max index of 3, we get 1 overshoot
    #   In that case, position_in_scale would calculate as 4 - (1 * 3) = 1
    overshoot = int(tone_index_in_octave / scale_indices)
    position_in_scale = tone_index_in_octave - (overshoot * scale_indices)

    # By now we know the position in the octave and how to divide that to get the 
    #   position in the scale. Thus we can get the scale tone for octave 0 
    #   by using scale[position_in_scale]. After that we can just add back
    #   all the octaves we've stripped away using overshoot and octave_index
    final = scale[position_in_scale] + ((overshoot + octave_index) * octave_len)

    # Return the scale determined tone value in the octave determined by overshoot
    return final

# Test to verify tones as expected for major scale
def test_scales():

    # The tones are as decoded from parsing lib, starting at A
    # A should be the first note in the third or fourth octave
    
    # Third octave: [36,37,38,39, 40,41,42,43 44,45,46,47]
    #                 c    d       e f     g     a     b  

    tones = [36,37,38,39, 40,41,42, 43]
    scale=[0,2,4,5,7,9,11]
    expected = [36,38,40,41, 43,45,47, 48]
    
    i = 0
    for tone in tones:
        result = transpose(tone, scale)
        if result != expected[i]:
            print("### ERROR: Tone " + str(tone) + " should become " + str(expected[i]) + ", not " + str(result))
            print("----------------------")
       
        i += 1
