import keyboard  # using module keyboard

from time import sleep
from scales import MAJOR, MINOR, transpose
from rest_client import play
from pretty_midi import note_number_to_hz
print("Testing...")

keys =       ['a','b','c','d','e','f','g','h','i','j','k']
press_keys = ['q','w','e','r','t','y','u','i','o','p','å']
octave_keys = [4,5,6,7,8]
octave = 11
current = 4
locks = []
synths = ["blipp", "FMRhodes1", "varsaw", "sinepad"]
selected_synth = 0


scale = MAJOR
# TODO: Doesn't clean manually after sus, thus cpu leak in prosc
while True:
    for key in press_keys:
        if keyboard.is_pressed(key):   
            if key not in locks:
                ordinal = press_keys.index(key)
                tone_index = ordinal
                final_tone = transpose(tone_index, scale) + (octave * (current+1))
                play(note_number_to_hz(final_tone), synths[selected_synth])
                locks.append(key)
                print("### " + str( keys[ordinal] ) + str(current) )
        elif key in locks:
            locks.remove(key)
    for key in octave_keys:
        if keyboard.is_pressed(key):
            current = key
    if keyboard.is_pressed('up'):
        if 'up' not in locks:
            selected_synth += 1
            if len(synths) <= selected_synth:
                selected_synth = 0
            locks.append('up')
    else:
        if 'up' in locks:
            locks.remove('up')
