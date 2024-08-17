# Sets up some sane defaults (routers, synths, samples) and then runs a .bbd file as described


from pythonosc.osc_packet import OscPacket
import time
from decimal import Decimal

import jdw_shuttle_lib.jdw_osc_utils as jdw_osc_utils
from shuttle_notation import Parser, ResolvedElement
import sample_reading
import default_synthdefs
from nrt_scoring import Score
import nrt_scoring


import client as my_client

import billboarding
import traceback


import os


"""

    ISSUES & FEATURES

    - BUG: First parts of alternations don't inherit their args properly 
        - Shuttle notation issue, example: (a (b / c)):amp4 <-- b does not get amp4
        - Update: Added a test in which at least suffix reading seems ok, see "g2 = section_parsing" 
            (a (1 / 0) b)c would give "c" to 1's history, at least 

    - Synths
        - generally just expanding the library with better stuff

    - Full billboarding support
        - Bonus: "replace this track with this if running other group" 
            -> As in "gain the external id" so that you can switch things mid play for shorter tracks

    - Keyboard 
        - Separate key backend parts of keys and use it to revive input_lab
        - Implement all different config messages  
        - TODO: Dot-in-string-on-loop-start

    - Delay Unification
        - Since Supercollider has an internal delay, it is impossible for jackdaw apps to know <exactly> when
            a note is played for the human ear. 
        - The only way to get anywhere near this is to emit some form of event in jdw_sc to the router when 
            a note <actually> plays, either going via supercollider callback or as a delay-send to router

    - CPU Usage
        - input_lab sits at a constant 33% and makes the fans run 
        - Sequencer eats a decent amount of CPU even when stopped
            -> Ideally it should have some kind of dead-poll that is a lot slower than the current 4ms             

    - Meta-sequencer as a new app
        - Longer notes in e.g. dev-diary, but this solves many composition issues wihtout 
            making the regular sequencer more complex 
        - Syntax? 
            >>> drum bass riff §4
            >>> drum bass chords §2
            ... doesn't have to be harder 

    - A return to Timeline Scores 
        ?? To better help construct longer compositions
        - STEPS:
            1. Brainstorm how and if the Tracker can be used to build longer sequences
                - Remember the old idea of first defining a sequence and then playing
                - So tracks can be defined as they are today, but then extended 
                - You can easily create a separate set of collections inside the Tracker for the Scoring purpose, 
                    so that existing functionality is not affected
                - tracks.score_into_bundles() ... 
                - repeat_until(len) is once again essential, so that you can say "play these tracks until x time"
                    - This also allows padding with silence to keep tracks an equal length


                - .break(name, parse, peers) can be a way of saying "play this once, creating a track for it at this time, with peers playing along"
        - Would the meta-sequencer be able to perhaps record or simplify this? To avoid reinventing the wheel? 
            - You have all the notes available at the start, but you might not want to read them too carefully?
            - You can technically reverse things the same way that the keyboard does, plus individual args. 
                -> You'd get pretty messed up code, but it would work
                -> Still, you can do this just fine in jdw-pycompose without involving another application 

        

    - Documentation and other Boring Stuff
        - shuttle notation (once we're happy with the syntax)
        - sequencer lib (no blocker)
        - jdw sc error proofing
        - sequencer and sc OSC-driven-configuration

"""


effect_billboard = """

# EFFECT ORDERING: 
# Assuming default s_new strategy (0): "add to head of group" 
# 1. Routers should be specified first (so as to be processed last)
# 2. Effects second
# Generally: In.ar(other) must be processed after (other)
# And with "add to head" that means "TYPE READERS BEFORE THEIR WRITERS"

# Routers created first, so as to appear last
@router tone:in10,out0
@router ttwo:in20,out0
@router tthr:in30,out0
@router tfou:in40,out0
@router tfiv:in50,out0
@router tsix:in60,out0
@router tsev:in70,out0
@router teight:in80,out0
@router tnin:in90,out0
@router tten:in92,out0
@router telv:in54,out0

@router routerrails:ofs0,sus10,amp1,bus80,in80,out0

@router tnin:in90,out0

"""

def read_bdd(bdd_name: str) -> billboarding.BillBoard:
    parser = Parser()
    parser.arg_defaults = {"time": Decimal("0.5"), "sus": Decimal("0.2"), "amp": Decimal("1.0")}

    path = os.path.dirname(os.path.realpath(__file__))
    content = open(path + "/" + bdd_name, 'r').read().replace("\\\n", "")
    return billboarding.parse_track_billboard(content, parser)

# TODO: COPY PASTE BAD CODE - only difference is the unfiltered call at end 
def read_bdd_nrt(bdd_name: str) -> billboarding.BillBoard:
    parser = Parser()
    parser.arg_defaults = {"time": Decimal("0.5"), "sus": Decimal("0.2"), "amp": Decimal("1.0")}

    path = os.path.dirname(os.path.realpath(__file__))
    content = open(path + "/" + bdd_name, 'r').read().replace("\\\n", "")
    return billboarding.parse_track_billboard_unfiltered(content, parser)

def error_beep():
    for i in [190.0, 300.0]:
        beep = jdw_osc_utils.create_msg("/note_on_timed", ["default", "error_beep", "0.1", 0, "freq", i, "amp", 1.0])
        my_client.get_default().send(beep)

def configure(bdd_name: str):
    try:

        billboard = read_bdd(bdd_name)
        keys_config_packets = billboarding.create_keys_config_packets(billboard)
        # legacy has the added function of being sent first (routers must be sent before other effects)
        legacy_effects = billboarding.parse_drone_billboard(effect_billboard, Parser())

        one_shot_messages = []

        client = my_client.get_default()

        client.send(jdw_osc_utils.create_msg("/set_bpm", [116]))

        # TODO: specific path read function would make things leaner and more direct 
        for sample in sample_reading.read_sample_packs("~/sample_packs"):
            client.send(jdw_osc_utils.create_msg("/load_sample", sample.as_args()))

        for synthdef in default_synthdefs.get():
            # TODO: Double check that the NRT synthdef array is not duplcicated iwth repeat calls 
            client.send(jdw_osc_utils.create_msg("/create_synthdef", [synthdef]))

        time.sleep(0.5)


        # Perform cleanup outside of other packet creation 
        common_prefix = "effect_"
        client.send(jdw_osc_utils.create_msg("/free_notes", ["^" + common_prefix + "(.*)"]))

        # Order is very important, but I get a headache trying to explain it 
        for oneshot in billboarding.create_effect_recreate_packets(legacy_effects, common_prefix):
            client.send(oneshot)

        for oneshot in billboarding.create_effect_recreate_packets(billboard.effects, common_prefix):
            client.send(oneshot)

        for oneshot in billboarding.create_effect_recreate_packets(billboard.drones, common_prefix):
            client.send(oneshot)


        for oneshot in keys_config_packets:
            client.send(oneshot)
    except Exception as e:
        print(traceback.format_exc())
        error_beep() 

# Create wav files for the base content of each track, regardless of composition and filtering 
def nrt_export(bdd_name: str):
    billboard = read_bdd_nrt(bdd_name)        
    
    client = my_client.get_default()

    # Send first, to populate the nrt synth predefineds
    # Can prob be done as messages within instead  ... .
    for synthdef in default_synthdefs.get():
        # TODO: Double check that the NRT synthdef array is not duplcicated iwth repeat calls 
        client.send(jdw_osc_utils.create_msg("/create_synthdef", [synthdef]))

    time.sleep(0.5)

    # TODO: specific path read function would make things leaner and more direct 
    for sample in sample_reading.read_sample_packs("~/sample_packs"):
        client.send(jdw_osc_utils.create_msg("/load_sample", sample.as_args()))

    time.sleep(0.5)

    # TODO: Below should to some degree be part of billboarding.py, but I'll make it all here first 

    # Preload the effect and drone rows for nrt, to avoid sending them with every nrt bundle 
    zero = get_nrt_base_msgs(billboard)
    client.send(jdw_osc_utils.create_msg("/clear_nrt", [])) # Wipe any previously exising nrt preload rows 
    time.sleep(0.05)
    for packet in zero:
        client.send(jdw_osc_utils.create_nrt_preload_bundle(packet))
        time.sleep(0.05)

    for track_name in billboard.tracks:
        billboard_track = billboard.tracks[track_name]

        # NOTE: Still does not account for e.g. reverb or delay 
        ring_out = float(billboard_track.elements[-1].args["sus"]) if len(billboard_track.elements) > 0 else 0.0 
        end_time = sum([float(e.args["time"]) for e in billboard_track.elements]) + ring_out # A little extra to ring out any sustains
        bpm = 116.0; # TODO: Hardcoded

        notes = billboarding.create_notes_b(billboard_track.elements, billboard_track.synth_name, billboard_track.is_sampler)
        if len(notes) > 0:
            score_notes = notes

            file_name = "/home/estrandv/jdw_output/track_" + track_name + ".wav"

            bundle = jdw_osc_utils.create_nrt_record_bundle(score_notes, file_name, end_time, bpm)
            time.sleep(0.5)
            client.send(bundle)

# Basically routers 
def get_legacy_effect_recreate_packets(billboard: billboarding.BillBoard):
    common_prefix = "effect_"
    legacy_effects: dict[str,BillboardEffect] = billboarding.parse_drone_billboard(effect_billboard, Parser())
    return billboarding.create_effect_recreate_packets(legacy_effects, common_prefix)

def get_nrt_base_msgs(billboard: billboarding.BillBoard):

    # Prefix is legacy and should be removed, more details in the packet fetchers 
    common_prefix = "effect_"

    zero_time = []
    # Order is very important, but I get a headache trying to explain it 
    for oneshot in get_legacy_effect_recreate_packets(billboard):
        zero_time.append(oneshot)

    for oneshot in billboarding.create_effect_recreate_packets(billboard.effects, common_prefix):
        zero_time.append(oneshot)

    for oneshot in billboarding.create_effect_recreate_packets(billboard.drones, common_prefix):
        zero_time.append(oneshot)

    return zero_time #[jdw_osc_utils.to_timed_osc("0.0", packet) for packet in zero_time]

# Create nrt record messages for each track, using order as dictated by ">>>" sequential group filters to construct the full composition of the song. 
# TODO: Currently limited by message size - see notes on buffering
def nrt_record(bdd_name: str):
    try:

        ### TODO: Moving forward with better splitting 
        """
            This is in reference to the below points on selective zero-time loading. 

            The core issue is that billboard data is not properly grouped:
                - Each SYNTH on the billboard has TRACKS and EFFECTS
                - Each TRACK has a GROUP (which CAN be shared with the SYNTH header (default))
                - So a billboard should be a list of SYNTH_SECTIONS containing tracks, effects and drones as children
                    - Making it easier to distinguish what is needed where
                - If this is handled, we can avoid loading too many synths and effects, BUT: 
                    -> It does not solve buffer redundancy 

            Buffer redundancy is a different beast: 
                - UPDATE: See below on snippets; the same is now impemented for nrt sample loads (wiped on clear_nrt)

            Note on synthdefs 
                - Since these are not packets (but native scd code), we cannot send them to NRT preload
                - Wiping them before NRT means we kinda mess up live coding (but this is def an option since ctrl+u will immediately restore things)
                - We an add a separate array for NRT synthdefs, that is ALSO loaded for the same messages but wiped with nrt wipe 
                    -> I'm gonna go with this for now, but the implicit nrt-ness might need some documentation todos
                    -> This is now implemented. clear_nrt will clear loaded synthdefs. 
        
        """

        all_bundles = []

        billboard = read_bdd_nrt(bdd_name)        
        
        client = my_client.get_default()


        time.sleep(0.5)

        # TODO: Below should to some degree be part of billboarding.py, but I'll make it all here first 

        # Make a score, to make timedElements, to make packets (that we can then combine with zero)
        score = Score({}, {})
        for track_name in billboard.tracks:
            track = billboard.tracks[track_name]
            score.add(track_name, track)

        # Walk through each section of group filters in order to create a chronological score 
        for group_filter in billboard.group_filters:
            
            groupless_tracks = [track_name for track_name in billboard.tracks if billboard.tracks[track_name].group_name == ""]
            score.extend_groups(group_filter, groupless_tracks)

        end_time = score.get_end_time() + 8.0 # A little extra 
        bpm = 116.0; # TODO: Hardcoded

        for track_name in score.tracks:
            billboard_track = billboard.tracks[track_name]

            # TODO: I think create_notes_nrt might be a bit dated now that I know times to be relative in jdw_sc
            notes = nrt_scoring.create_notes_nrt(score.tracks[track_name], billboard_track.synth_name, billboard_track.is_sampler)

            #print(track_name, "TRACK TOTAL LEN", nrt_scoring.track_len(score.tracks[track_name]))

            if len(notes) > 0 and not nrt_scoring.all_quiet(score.tracks[track_name]):

                # NRT messages can get very large if all needed data is included in the message
                # Instead, we preload what we can via the regular methods, first clearing anything pre-existing
                # Filtering by context helps reduce redundancy

                client.send(jdw_osc_utils.create_msg("/clear_nrt", [])) # Wipe any previously exising nrt preload rows 
                time.sleep(0.1)

                # TODO: Synthdef filtering doesn't work because effects are lumped in with regular synths 
                # Putting a hack in here now using "In.ar()" as effect detection, but long term they should be separated
                effect_tag = "In.ar("

                if billboard_track.is_sampler:
                    ### PRELOAD SAMPLES 
                    for sample in sample_reading.read_sample_packs("~/sample_packs"):
                        # Hack: check if sample pack is relevant, given the track header info 
                        if sample.sample_pack in billboard_track.synth_name:
                            client.send(jdw_osc_utils.create_msg("/load_sample", sample.as_args()))
                    
                    # Hack: Just in case we've redefined the default "sampler" synth here, include the overwrite for sampler tracks
                    for synthdef in default_synthdefs.get():
                        # No need to load snippets that don't contain the active synth name
                        if "sampler" in synthdef or effect_tag in synthdef:
                            client.send(jdw_osc_utils.create_msg("/create_synthdef", [synthdef]))

                else:
                    ### PRELOAD SYNTHDEFS 
                    for synthdef in default_synthdefs.get():
                        # No need to load snippets that don't contain the active synth name
                        if billboard_track.synth_name in synthdef or effect_tag in synthdef:
                            client.send(jdw_osc_utils.create_msg("/create_synthdef", [synthdef]))

                # TODO: CBA checkin all the sleeps make sense, go through later
                time.sleep(0.05)

                ### PRELOAD EFFECTS AND DRONES
                
                # TODO: Skip all but relevant for particular track
                # This will make a lot of noise about missing synthdefs for drones 
                zero = get_nrt_base_msgs(billboard)
                for packet in zero:
                    client.send(jdw_osc_utils.create_nrt_preload_bundle([packet]))
                    time.sleep(0.05)

                score_notes = notes

                file_name = "/home/estrandv/jdw_output/track_" + track_name + ".wav"

                bundle = jdw_osc_utils.create_nrt_record_bundle(score_notes, file_name, end_time, bpm)

                all_bundles.append(bundle)

                # Might help if dropping packets is ever the issue 
                #time.sleep(2.25)

                client.send(bundle)

            else:
                print("WARN: Empty track will not be sent to NRT", track_name, score.tracks[track_name])


        #client.send(jdw_osc_utils.create_batch_bundle(all_bundles))
            
    except Exception as e:
        print(traceback.format_exc())
        error_beep() 


def run(bdd_name: str):

    client = my_client.get_default()

    try: 

        billboard = read_bdd(bdd_name)
        keys_config_packets = billboarding.create_keys_config_packets(billboard)

        # TODO: Include in billboard somehow 
        keys_config_packets.append(jdw_osc_utils.create_msg("/keyboard_quantization", ["0.25"]))

        # legacy has the added function of being sent first (routers must be sent before other effects)
        legacy_effects = billboarding.parse_drone_billboard(effect_billboard, Parser())

        for packet in billboarding.create_effect_mod_packets(legacy_effects, "fx_old_"):
            client.send(packet)

        for packet in billboarding.create_effect_mod_packets(billboard.effects) + keys_config_packets:
            client.send(packet)

        queue_bundle = billboarding.create_sequencer_queue_bundle(billboard.tracks, True)

        client.send(queue_bundle)
    except Exception as e:
        print(traceback.format_exc())
        error_beep() 

    # Useful in the past, not as important now with batch sending
    #client.send_message("/wipe_on_finish", [])
