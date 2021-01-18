from __future__ import annotations # Not needed after python 3.10

import jackdaw
from copy import deepcopy
from pretty_midi.utilities import note_number_to_hz

from scales import transpose

import json
import requests
import random 

def parse(note_string: str) -> List[Dict]:
    notes = jackdaw.parse(note_string)
    return notes

class Score:
    def __init__(self):
        self.notes: List[Dict] = []
        self._latest_note_string = ""

    def len(self) -> float:
        return sum([e['reserved_time'] for e in self.notes])

    # Add silent notes equivalent to the provided beats
    def pad(self, beats: float):
        self.notes.append({'tone':0,'sustain_time':0.0,'reserved_time':beats,'amplitude':0.0})
        return self 

    def play(self, note_string: str):
        self.notes = self.notes + parse(note_string)
        self._latest_note_string = note_string
        return self 

    def join(self, other: Score):
        self.notes = self.notes + other.notes
        return self 

    # Debug function for reach()
    def peek_notes(self):
        print([n["tone"] for n in self.notes])
        return self 

    # Recursive function to repeat the original loop until len reaches
    # that of other. If a repeat of the original would surpas len of other,
    # a pad is done instead.
    def reach(self, length: float):

        # Empty score objects should stay that way
        if (self.len() == 0.0):
            self.pad(length)

        if self.len() < length:
            self.play(self._latest_note_string)
            if self.len() <= length:
                self.reach(length)
            else:
                self.pad(length - self.len())
        else:
            return self

    # Apply the scales.py scale to the parsed notes
    def scale(self, scale: List[int]):
        for note in self.notes:
            note["tone"] = transpose(note["tone"], scale)
        return self 

    # Translate note tones to a viable format prior to sending 
    def _prepare(self, to_hz: bool):
        # Replace note indices with actual hz
        for note in self.notes:
            if to_hz:
                note["tone"] = note_number_to_hz(note["tone"])
            else:
                # jdw-sequencer expects float/decimal format for tone, even when not in hz
                note["tone"] = float(note["tone"])

    ### Rest call stuff

    def post_sample(self, name: str, key: str):
        self._prepare(False)
        response = requests.post(
            'http://localhost:8000/queue/prosc_sample/'+ key + '/' + name,
            json=self.notes
        )

    def post(self, name: str, key: str):
        self._prepare(False)
        response = requests.post(
            'http://localhost:8000/queue/midi/'+ key + '/' + name,
            json=self.notes
        )    

    def post_prosc(self, name: str, key: str):
        self._prepare(True)
        response = requests.post(
            'http://localhost:8000/queue/prosc/'+ key + '/' + name,
            json=self.notes
        )