# todo: WIP translation to be used with new billboarding

from decimal import Decimal
from pythonosc.osc_bundle import OscBundle
from shuttle_notation.parsing.element import ResolvedElement
from jdw_osc_utils import ElementMessage, create_msg, to_timed_osc
from dataclasses import dataclass, field

from parsing import BillboardTrack

def element_beats(element: ElementMessage) -> Decimal:
    return Decimal(element.get_time())

def source_len(elements: list[ElementMessage]) -> Decimal:
    res = sum([element_beats(element) for element in elements])
    return res if isinstance(res, Decimal) else Decimal("0.0")

@dataclass
class TrackSource:
    elements: list[ElementMessage]
    group_name: str

# NONE allows for silece padding
@dataclass
class ScoreMessage:
    message: ElementMessage | None
    time: Decimal

def total_beats(elements: list[ScoreMessage]) -> Decimal:
    res = sum([element.time for element in elements])
    return res if isinstance(res, Decimal) else Decimal("0.0")

@dataclass
class Score:
    track_sources: dict[str, TrackSource] = field(default_factory=dict)
    tracks: dict[str, list[ScoreMessage]] = field(default_factory=dict)

    # Export a finished set of tracks from the modifications done by extend() and pad()
    def unpack_timed_tracks(self) -> dict[str, list[OscBundle]]:
        export_dict: dict[str, list[OscBundle]] = {}

        # Compress messages so that silence gets appended to the previous note
        # This declutters the final score object in supercollider but isn't strictly important
        # TODO: Destructive operation, maybe place elsewhere
        for track_name in self.tracks:

            new_set: list[ScoreMessage] = []

            for msg in self.tracks[track_name]:
                if not isinstance(msg.message, ElementMessage):
                    if len(new_set) > 0:
                        new_set[-1].time += msg.time
                    else:
                        new_set.append(msg)
                else:
                    new_set.append(msg)

            self.tracks[track_name] = new_set

        for track_name in self.tracks:
            export_dict[track_name] = []
            for msg in self.tracks[track_name]:
                if isinstance(msg.message, ElementMessage):
                    timed_bundle = to_timed_osc(str(msg.time.normalize()), msg.message.osc)
                    export_dict[track_name].append(timed_bundle)
                else:
                    timed_bundle = to_timed_osc(str(msg.time.normalize()), create_msg("/empty_message", []))
                    export_dict[track_name].append(timed_bundle)

        return export_dict

    def add_source(self, track_name: str, track_group: str, elements: list[ElementMessage]):
        self.track_sources[track_name] = TrackSource(elements, track_group)
        self.tracks[track_name] = []

    def extend_track(self, track_name: str):
        source_track = self.track_sources[track_name]
        timeline_track = self.tracks[track_name]

        for ele in source_track.elements:
            timeline_track.append(ScoreMessage(ele, element_beats(ele)))

    def pad_track(self, track_name: str, beats: Decimal):
        self.tracks[track_name].append(ScoreMessage(None, beats))

    def get_end_time(self):
        return max([total_beats(self.tracks[track_name]) for track_name in self.tracks])

    def extend_groups(self, group_names: list[str], also_extend_groupless: bool = True):

        def track_conforms(tname: str, gname: str):
            return len(group_names) == 0 or (gname == "" and also_extend_groupless) or (gname in group_names)

        # Determine tracks to extend
        track_names = [key for key in self.track_sources if track_conforms(key, self.track_sources[key].group_name)]


        if len(track_names) == 0:
            print("WARN: no track conforms to group filter", group_names)
            return

        # Determine longest extending source material
        longest_track_name = None
        for key in track_names:

            cur_longest = source_len(self.track_sources[longest_track_name].elements) if longest_track_name != None else Decimal("0.0")

            this_len = source_len(self.track_sources[key].elements)


            if this_len > cur_longest:
                longest_track_name = key

        if isinstance(longest_track_name, str):
            self.extend_track(longest_track_name)
            goal_time = total_beats(self.tracks[longest_track_name])


            for track_name in self.track_sources:
                slen = source_len(self.track_sources[track_name].elements)

                if track_name != longest_track_name:

                    if total_beats(self.tracks[track_name]) < goal_time:
                        while total_beats(self.tracks[track_name]) < goal_time:
                            diff = goal_time - total_beats(self.tracks[track_name])

                            #if diff < slen and track_name in track_names:
                                #print("Can't extend ", track_name, diff, slen)

                            if diff >= slen and track_name in track_names:

                                self.extend_track(track_name)
                                #print("Extended and now has these elements", len(self.tracks[track_name]))
                            else:
                                self.pad_track(track_name, diff)
