# Library for effective reconstruction of billboards as NRT definitions

from billboarding import BillboardTrack
from dataclasses import dataclass
from shuttle_notation import Parser, ResolvedElement

# Stolen from billboarding's create notes function

# TODO: YOU ARE HERE, SORTA. JUST FINISHED THIS FOR USE WITH RESOLVED TIMELINES IN RUN_BILLBOARDING. 
# I THINK WE HAVE ALL PIECES, BUT THEY HAVE TO COME TOGETHER. INCLUDING MAKING ALL ZERO TIME MESSAGES TimelineElement with time 0.0 
def create_notes_nrt(elements: list[TimelineElement], synth_name, is_sample = False) -> list[OscBundle]:
    sequence = []
    for timeline_element in elements:

        element = timeline_element.element

        wrapper = ElementWrapper(element, synth_name, MessageType.PLAY_SAMPLE if is_sample else MessageType.NOTE_ON_TIMED)
        
        msg = jdw_osc_utils.resolve_jdw_msg(wrapper)

        if msg != None:

            timed = jdw_osc_utils.to_timed_osc(str(timeline_element.start_time), msg)

            sequence.append(timed)

    return sequence

def element_beats(element: ResolvedElement) -> float:
    value = float(element.args["time"].value) if "time" in element.args else 0.0
    return value 

def total_beats(elements: list[ResolvedElement]) -> float:
    return sum([element_len(element) for element in elements])

def track_len(track: list[TimelineElement]) -> float:
    return max([t.end_time for t in track]) if len(track) > 0 else 0.0  

@dataclass
class TimelineElement:
    element: ResolvedElement
    start_time: float
    end_time: float 

@dataclass
class Score:
    source_tracks: dict[str, BillboardTrack]
    tracks: dict[str, list[TimelineElement]]

    def add(self, track_name: str, track: BillboardTrack):
        self.source_tracks[track_name] = track 
        self.tracks[track_name] = []

    # Plays the given track once 
    # NOTE: elements can be referenced by many timelineElements - revisit with deepCopy() if this becomes a problem
    def extend(self, track_name: str):
        source_track = self.source_tracks[track_name]
        timeline_track = self.source_tracks[track_name]
        
        timeline = track_len(timeline_track)
        for ele in source_track.elements:
            new_ele = TimelineElement() 
            new_ele.start_time = timeline
            timeline += element_beats(ele)
            new_ele.end_time = timeline
            new_ele.element = ele 
            timeline_track.append(new_ele)

    # Pads the track with silence 
    def pad(self, track_name: str, beats: float):
        timeline_track = self.source_tracks[track_name]
        
        timeline = track_len(timeline_track) 

        # TODO: Best if TimelineElement gets treated as having an OPTIONAL element, so that we can do this: 
        padding = TimelineElement() 
        padding.start_time = timeline
        padding.end_time = timeline + beats 

        timeline_track.append(padding)

    # Extend tracks that conform to group, pad the rest to match new timeline len 
    def extend_groups(self, group_names: list[str]):
        
        # Determine tracks to extend
        track_names = [key for key in self.source_tracks if self.source_tracks[key].group_name in group_names]
        
        # Determine longest extending source material 
        longest_track_name = track_names[0]
        for key in track_names:
            if total_beats(self.source_tracks[key].elements) > total_beats(self.source_tracks[longest_track_name].elements):
                longest_track_name = key
        
        # Start by extending the longest track
        self.extend(longest_track_name)

        goal_time = track_len(self.tracks[longest_track_name])

        for track_name in self.source_tracks:
            source_len = total_beats(self.source_tracks[track_name].elements)

            if track_name != longest_track_name:

                if track_len(self.tracks[track_name]) < goal_time:
                    while track_len(self.tracks[track_name]) < goal_time:
                        diff = goal_time - track_len(self.tracks[track_name])
                        # Only group-filtered tracks are eligible for extension
                        if diff <= source_len and track_name in track_names:
                            self.extend(track_name)
                        else:
                            self.pad(track_name, diff)
