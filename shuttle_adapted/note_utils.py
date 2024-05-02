from shuttle_notation import ResolvedElement
from decimal import Decimal
from pretty_midi import note_number_to_hz


def resolve_freq(element: ResolvedElement) -> float:
    if "freq" in element.args:
        return float(element.args["freq"])
    
    letter_check = note_letter_to_midi(element.prefix)

    if letter_check == -1:

        # Placeholders 
        octave = 3
        scale = scales.MAJOR

        extra = (12 * (octave + 1)) if octave > 0 else 0
        new_index = element.index + extra
        # TODO: port transpose from scales.py 
        #new_index = transpose(new_index, scale)
        freq = note_number_to_hz(new_index)
        return freq 

    else:
        # E.g. "C" or "C#" or "Cb"
        letter_and_semitone = element.prefix.lower() 
        # As in the "3" of "c3"
        octave = element.index if element.index != None else 1

        # Math, same as for index freq calculation
        extra = (12 * (octave + 1)) if octave > 0 else 0
        new_index = letter_check + extra

        return note_number_to_hz(new_index)

def note_letter_to_midi(note_string) -> int:
    # https://stackoverflow.com/questions/13926280/musical-note-string-c-4-f-3-etc-to-midi-note-value-in-python
    # [["C"],["C#","Db"],["D"],["D#","Eb"],["E"],["F"],["F#","Gb"],["G"],["G#","Ab"],["A"],["A#","Bb"],["B"]]
    note_map = {
        "c": 0,
        "c#": 1,
        "db": 1,
        "d": 2,
        "d#": 3,
        "eb": 3,
        "e": 4,
        "f": 5,
        "f#": 6,
        "gb": 6,
        "g": 7,
        "g#": 8,
        "ab": 8,
        "a": 9,
        "a#": 10,
        "bb": 10,
        "b": 11
    }

    if note_string in note_map:
        return note_map[note_string]
    else:
        return -1
