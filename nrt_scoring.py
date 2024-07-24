# Library for effective reconstruction of billboards as NRT definitions

from billboarding import BillboardTrack
from dataclasses import dataclass
from shuttle_notation import Parser, ResolvedElement
from pythonosc.osc_bundle import OscBundle
from jdw_shuttle_lib.shuttle_jdw_translation import ElementWrapper
from jdw_shuttle_lib.shuttle_jdw_translation import MessageType
import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils


@dataclass
class TimelineElement:
    element: ResolvedElement
    start_time: float
    end_time: float 

def all_quiet(elements: list[TimelineElement]):
    return len([e for e in elements if e.element != None]) == 0

# Stolen from billboarding's create notes function
def create_notes_nrt(elements: list[TimelineElement], synth_name, is_sample = False) -> list[OscBundle]:

    # It's a mess ... But empty element means silence here and we need to account for that. 
    def e_to_msg(emnt):

        if emnt == None:
            return jdw_osc_utils.create_msg("/empty_msg", [])
        else:
            wrapper = ElementWrapper(emnt, synth_name, MessageType.PLAY_SAMPLE if is_sample else MessageType.NOTE_ON_TIMED)
            return jdw_osc_utils.resolve_jdw_msg(wrapper)


    sequence = []
    for timeline_element in elements:

        msg = e_to_msg(timeline_element.element)

        if msg != None:

            # JDW-SC already accounts for relative start times, but we need to account for silences 
            rel_time = timeline_element.end_time - timeline_element.start_time
            timed = jdw_osc_utils.to_timed_osc(str(rel_time), msg)

            sequence.append(timed)

    return sequence

def element_beats(element: ResolvedElement) -> float:
    value = float(element.args["time"]) if "time" in element.args else 0.0
    return value 

def total_beats(elements: list[ResolvedElement]) -> float:
    return sum([element_beats(element) for element in elements])

def track_len(track: list[TimelineElement]) -> float:
    return max([t.end_time for t in track]) if len(track) > 0 else 0.0  

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
        timeline_track = self.tracks[track_name]
        
        timeline = track_len(timeline_track)
        for ele in source_track.elements:
            prev_timeline = float(timeline)
            timeline += element_beats(ele)
            new_ele = TimelineElement(ele, prev_timeline, float(timeline))
            timeline_track.append(new_ele)

    # Pads the track with silence 
    def pad(self, track_name: str, beats: float):
        timeline_track = self.tracks[track_name]
        
        timeline = track_len(timeline_track) 

        padding = TimelineElement(None, timeline, timeline + beats) 

        timeline_track.append(padding)

    def get_end_time(self):
        longest = None 
        for key in self.tracks:
            track = self.tracks[key]

            current = track_len(track)

            if longest == None or (current > longest):
                longest = current

        return longest if longest != None else 0.0

    # Extend tracks that conform to group, pad the rest to match new timeline len 
    def extend_groups(self, group_names: list[str], static_track_names: list[str] = []):

        def track_conforms(tname, gname):
            return len(group_names) == 0 or (tname in static_track_names) or (gname in group_names)

        # Determine tracks to extend
        track_names = [key for key in self.source_tracks if track_conforms(key, self.source_tracks[key].group_name)]

        if len(track_names) == 0:
            print("WARN: no track conforms to group filter", group_names)
            return 

        # Determine longest extending source material 
        longest_track_name = None
        for key in track_names:

            cur_longest = total_beats(self.source_tracks[longest_track_name].elements) if longest_track_name != None else 0.0 

            if total_beats(self.source_tracks[key].elements) > cur_longest:
                longest_track_name = key
        
        # Start by extending the longest track
        self.extend(longest_track_name)

        goal_time = track_len(self.tracks[longest_track_name])
        #print(longest_track_name, "is longest at ", goal_time)

        for track_name in self.source_tracks:
            source_len = total_beats(self.source_tracks[track_name].elements)

            if track_name != longest_track_name:

                if track_len(self.tracks[track_name]) < goal_time:
                    while track_len(self.tracks[track_name]) < goal_time:
                        diff = goal_time - track_len(self.tracks[track_name])

                        if diff < source_len and track_name in track_names:
                            print("Can't extend ", track_name, diff, source_len)

                        if diff >= source_len and track_name in track_names:

                            self.extend(track_name)
                        else:    
                            self.pad(track_name, diff)
