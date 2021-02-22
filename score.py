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
    print(notes)
    return notes

class Score:
    def __init__(self):
        self.notes: List[Dict] = []
        self._latest_note_string = ""

    def len(self) -> float:
        return sum([e['reserved_time'] for e in self.notes])

    # Add silent notes equivalent to the provided beats
    def pad(self, beats: float):
        # No need to add worthless padding notes
        if beats > 0.0:
            self.notes.append({'tone':0,'sustain_time':0.0,'reserved_time':beats,'amplitude':0.0})
        return self 

    def play(self, note_string: str):
        self.notes = self.notes + parse(note_string)
        self._latest_note_string = note_string
        return self 

    def play_latest(self):
        self.notes = self.notes + parse(self._latest_note_string)
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

        # Empty score objects should stay that way. Note how 0.0 means we pad the full amount.
        if (self.len() == 0.0):
            self.pad(length)

        if self.len() < length:

            diff = length - self.len()
            next_play = Score() # Use a score object to preview play length
            next_play.play(self._latest_note_string)
            
            # If playing once would not overshoot the target length
            if self.len() + next_play.len() <= length:
                self.play(self._latest_note_string)
                self.reach(length)
            else:
                print("Padding: " + self._latest_note_string)
                self.pad(diff)
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


    def get_messages(self, synth):

        def to_value(key, value):
            val = {}
            val["name"] = key 
            val["value"] = value
            return val 
    

        msgs = []
        for note in self.notes:
            message = {}
            values = []
            values.append(to_value("amp", note["amplitude"]))
            values.append(to_value("sus", note["sustain_time"]))
            values.append(to_value("reserved_time", note["reserved_time"]))
            values.append(to_value("freq", note["tone"]))
            message["values"] = values
            message["synth"] = synth
            msgs.append(message)

        return msgs
            

    ### Rest call stuff

    def post_sample(self, name: str, key: str):
        self._prepare(False)
        response = requests.post(
            'http://localhost:8000/queue/prosc_sample/'+ key + '/' + name,
            json=self.get_messages(key)
        )

    def post(self, name: str, key: str):
        self._prepare(False)
        response = requests.post(
            'http://localhost:8000/queue/midi/'+ key + '/' + name,
            json=self.get_messages(key)
        )    

    def post_prosc(self, name: str, key: str):
        self._prepare(True)
        response = requests.post(
            'http://localhost:8000/queue/prosc/'+ key + '/' + name,
            json=self.get_messages(key)
        )
