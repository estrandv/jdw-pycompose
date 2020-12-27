from __future__ import annotations # Not needed after python 3.10

import jackdaw
from copy import deepcopy
from pretty_midi.utilities import note_number_to_hz

import json
import requests
import random 

def parse(note_string: str, to_hz: bool = True) -> List[Dict]:
    notes = jackdaw.parse(note_string)
    # Replace note indices with actual hz
    for note in notes:
        if to_hz:
            note["tone"] = note_number_to_hz(note["tone"])
        else:
            # jdw-sequencer expects float/decimal format for tone, even when not in hz
            note["tone"] = float(note["tone"])
    return notes


class Score:
    def __init__(self, note_string: str = "", to_hz: bool = True):
        self.notes: List[Dict] = parse(note_string, to_hz)
        self._original: str = note_string
        self.to_hz = to_hz

    def len(self) -> float:
        return sum([e['reserved_time'] for e in self.notes])

    # Add silent notes equivalent to the provided beats
    def pad(self, beats: float) -> Score: # Returns padded Score copy
        padded = deepcopy(self)
        padded.notes.append({'tone':0,'sustain_time':0.0,'reserved_time':beats,'amplitude':0.0})
        return padded

    def plus(self, note_string: str) -> Score: # Returns copy with notes at end
        extended = deepcopy(self)
        extended.notes = extended.notes + parse(note_string, to_hz=self.to_hz)
        return extended

    def join(self, other: Score) -> Score:
        joined = deepcopy(self)
        joined.notes = joined.notes + other.notes
        return joined

    # Debug function for reach()
    def peek_notes(self) -> Score:
        print([n["tone"] for n in self.notes])
        return self

    # Recursive function to repeat the original loop until len reaches
    # that of other. If a repeat of the original would surpas len of other,
    # a pad is done instead.
    def reach(self, length: float) -> Score:

        # Empty score objects should stay that way
        if (self.len() == 0.0):
            return self.pad(length)

        if self.len() < length:
            s = self.plus(self._original)
            if s.len() <= length:
                return s.reach(length)
            else:
                return s.pad(length - self.len())
        else:
            return self

    ### Rest call stuff

    def post_sample(self, name: str, key: str):
        response = requests.post(
            'http://localhost:8000/queue/prosc_sample/'+ key + '/' + name,
            json=self.notes
        )

    def post(self, name: str, key: str):
        response = requests.post(
            'http://localhost:8000/queue/midi/'+ key + '/' + name,
            json=self.notes
        )    

    def post_prosc(self, name: str, key: str):
        response = requests.post(
            'http://localhost:8000/queue/prosc/'+ key + '/' + name,
            json=self.notes
        )