from __future__ import annotations # Not needed after python 3.10

from score import Score
import pscore
import rest_client

class Composer:
    def __init__(self):
        self.score_data_list: list[ScoreData] = []

    # Create a new score and keep the reference
    def new(self, id: str, instrument: str, posting: PostingType) -> pscore.Score:
        added = ScoreData(pscore.Score(),id,instrument,posting)
        self.score_data_list.append(added)
        return added.score
        
    # Pad all contained scores with silence until they are all the same length
    def sync(self):
        for score in self.score_data_list:
            diff = self.len() - score.score.len()
            if diff > 0.0:
                score.score.pad(diff)

    def play(self, *scores):
        for score in scores:
            score.play_latest().reach(self.len())

    def len(self):
        longest = 0.0
        for score in self.score_data_list:
            if score.score.len() > longest:
                longest = score.score.len()
        return longest

    def post_all(self):
        for data in self.score_data_list:

            if data.posting == PostingTypes.PROSC:
                rest_client.post_prosc(data.id, data.instrument, data.score.export(data.instrument))
            if data.posting == PostingTypes.MIDI:
                rest_client.post_midi(data.id, data.instrument, data.score.export(data.instrument))
            if data.posting == PostingTypes.SAMPLE:
                rest_client.post_sample(data.id, data.instrument, data.score.export(data.instrument))

    # Wipe data up until this point
    def start_here(self):
        for data in self.score_data_list:
            data.score.notes = []

class ScoreData:
    def __init__(self, score: pscore.Score, id: str, instrument: str, posting: PostingType):
        self.score: Score = score
        self.id = id 
        self.instrument = instrument
        self.posting = posting

class PostingType:

    def __init__(self, id: int):
        self.id = id

class PostingTypes:
    PROSC = PostingType(0)
    SAMPLE = PostingType(1)
    MIDI = PostingType(2)
