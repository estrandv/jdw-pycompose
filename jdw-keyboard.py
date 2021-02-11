from time import sleep
import keyboard
from scales import MAJOR, MINOR, transpose
from rest_client import play
from pretty_midi import note_number_to_hz
import pandas as pd 

print("Press enter to record a sequence or display the last one")

keys =       ['a','b','c','d','e','f','g','h','i','j','k']
press_keys = ['q','w','e','r','t','y','u','i','o','p','å']
octave_keys = [4,5,6,7,8]
octave = 11
current = 4
locks = []
synths = ["blipp", "FMRhodes1", "varsaw", "sinepad"]
selected_synth = 0
scales = [MAJOR, MINOR]

sustain = 1.0

sequence = []

def press_check(key) -> bool:
    if keyboard.is_pressed(key):
        if key not in locks:
            locks.append(key)
            return True
    elif key in locks:
        locks.remove(key)
    return False

scale = 0
while True:
    for key in press_keys:
        if press_check(key):
            ordinal = press_keys.index(key)
            tone_index = ordinal
            final_tone = transpose(tone_index, scales[scale]) + (octave * (current))
            play(note_number_to_hz(final_tone), synths[selected_synth], sustain)
            sequence.append( str( keys[ordinal] ) + str(current) )
    for key in octave_keys:
        if keyboard.is_pressed(key):
            current = key
            print("# CURRENT OCTAVE: " + str(current))
    if press_check('up') and keyboard.is_pressed('ctrl'):
        selected_synth += 1
        if len(synths) <= selected_synth:
            selected_synth = 0
        print("Synth: " + synths[selected_synth])
    if press_check('s'): 
        sustain += 0.1
        print(str(sustain))
        sleep(0.1)
    if press_check('a'):
        sustain -= 0.1
        print(str(sustain))
        sleep(0.1)
    if press_check('enter'):
        out = ' '.join(sequence)
        print("\"" + out + "\" copied to clipboard")
        df=pd.DataFrame([out])
        df.to_clipboard(index=False,header=False)
        sequence = []
            
