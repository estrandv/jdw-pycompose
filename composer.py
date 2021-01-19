from __future__ import annotations # Not needed after python 3.10

from score import Score

class Composer:
    def __init__(self):
        self.score_data_list = []

    # Create a new score and keep the reference
    def new(self, id: str, instrument: str, posting: PostingType) -> Score:
        added = ScoreData(Score(),id,instrument,posting)
        self.score_data_list.append(added)
        return added.score
        
    # Pad all contained scores with silence until they are all the same length
    def sync(self):
        for score in self.score_data_list:
            score.score.pad(self.len() - score.score.len())

    def len(self):
        longest = 0.0
        for score in self.score_data_list:
            if score.score.len() > longest:
                longest = score.score.len()
        return longest

    def post_all(self):
        for data in self.score_data_list:
            if data.posting == PostingTypes.PROSC:
                data.score.post_prosc(data.id, data.instrument)
            if data.posting == PostingTypes.MIDI:
                data.score.post(data.id, data.instrument)
            if data.posting == PostingTypes.SAMPLE:
                data.score.post_sample(data.id, data.instrument)

    # Wipe data up until this point
    def start_here(self):
        for data in self.score_data_list:
            data.score.notes = []

class ScoreData:
    def __init__(self, score: Score, id: str, instrument: str, posting: PostingType):
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