# Testing grounds 
from osc_transform import SendType, create_msg, MessageWrapper, to_timed_osc
from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
import parsing
from pythonosc import udp_client


client = udp_client.SimpleUDPClient("127.0.0.1", 13339) # Router
client.send(create_msg("/set_bpm", [120]))


class Synth():
    def __init__(self, parse: str, ext_id = ""):

        # TODO: Most of tis copy pasted from (replacing) sender.send() 

        # TODO: Could also be a builder method with this as default 
        if ext_id == "": 
            ext_id = "autogen_queue_id_" + str(uuid.uuid4())

        self.ext_id = ext_id

        messages = parsing.full_parse(parse)

        self.msg_wrappers = []
        for msg in messages: 
            msg.add_missing_args({"time": 1.0, "gate_time": 0.1, "amp": 1.0})
            self.msg_wrappers.append(MessageWrapper(msg))

    def nrt_record(self, synth: str, default_type = SendType.NOTE_ON_TIMED):
        main_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)

        bun = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        
        timeline = 0
        for wrapper in self.msg_wrappers:

            send_msg = wrapper.to_osc(default_type, synth)

            # TODO: With wrapper resolving the above internally, you can also do this baking 
            print("DEBUG: resolved time on message: ", str(wrapper.get_time()))
            wrp = to_timed_osc(wrapper.get_time(), send_msg)
            bun.add_content(wrp)
            timeline += wrapper.get_time()


        main_bundle.add_content(create_msg("/bundle_info", ["nrt_record"]))
        main_bundle.add_content(create_msg("/nrt_record_info", [120.0, self.ext_id + ".wav", timeline]))
        main_bundle.add_content(bun.build())

        # TODO: Global client 
        client.send(main_bundle.build())


    # TODO: play/play_sample might be simpler than default type
    # But you can easily make those call this 
    def play(self, synth: str, default_type = SendType.NOTE_ON_TIMED):

        main_bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        main_bundle.add_content(create_msg("/bundle_info", ["update_queue"]))
        # NOTE: Meta-info for the update-queue command, mainly the external id of the sequencer 
        main_bundle.add_content(create_msg("/update_queue_info", [self.ext_id]))

        bun = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        for wrapper in self.msg_wrappers:

            send_msg = wrapper.to_osc(default_type, synth)


            # TODO: With wrapper resolving the above internally, you can also do this baking 
            print("DEBUG: resolved time on message: ", str(wrapper.get_time()))
            wrp = to_timed_osc(wrapper.get_time(), send_msg)
            bun.add_content(wrp)
        main_bundle.add_content(bun.build())

        # TODO: Global client 
        client.send(main_bundle.build())

Synth("bd0 (hh0/hh0[ofs0]) bd4 (hh0/(hh0 hh4)[=0.5])", "drum2").nrt_record("KorgT3", SendType.PLAY_SAMPLE)
#Synth("bd0 hh2 bd0 hh4", "drum2").nrt_record("KorgT3", SendType.PLAY_SAMPLE)
#Synth("cy1[=16 #0.2]", "drm").play("example", SendType.PLAY_SAMPLE)
#Synth(" (32) _ _ _ :: >0.1 #0.2 =0.25 relT0.2", "drill").play("brute")
#Synth("2 _ 2 2 4 _ 4 4 3 _ 3 3 1 _ 1 1 :: #0.4 >0.1 =0.5 relT0.2", "bass").play("brute")
Synth(" (11/13/11/12)[=0 >2 relT2 #0.2] 7 9[=0.5] 8 5 _ 9 6 (2/(8 9)[=0.25])[=0.5] :: #0.3 >0.1 =0.5 relT0.2", "solo").nrt_record("brute")
#Synth(" 7 8 7 9 7 8 7 9 :: #0.3 >0.1 =0.25 relT0.2", "solo").nrt_record("brute")

# TODO: Something very clearly goes wrong here, somewhere
# Seems that queueing a certain kind of long-running note will cause arrythmia
# You can have a million things running at the same pace, but when one differing bugger is introduced late things get uneven
# Seems more to do with individual notes than total length of the sequence 
# If something triggers fucked-up state, you can then not include it in the next send and things can go back to normal 
# As if the queue call itself messes things up, regardless of it being identical to pre-existing 
# This could well be due to some issue with this library rather than the sequencer itself 
# Super simple example below: longer sequence only works when shorter is commented (but already running)

# Investigatin
# - Kept an eye on logs - seems both are indeed sending but the one with more noes comes in batches in sync with the first one's tick
# - Confirmed not a part of the new started=false fix
# - Not immediately obvious as a start/reset mode bug, but reset_together might have made slightly different noises (in same tempo, thou)
# - Made a log as "playing notes for" that doesnt seem to trigger for both even when it SOUNDS ok 
# - Found the case! When one sequencer only has one note, things get hairy! Even adding with a silent one is fine. 
# - Found no evidence of missed indices or suchlike in the code - end_beat should be correct 
# - Something DOES mess with end_beat however, doubling it in some cases
# - Moved the = arg from :: to [] for the single-note and things appear ok now... 
# - Must be something with the parsing lib, but still does not explain why comment+resend works even with :: 
# - Also: Even with [] instead of ::, sequencer only lists arg2 as being played
# - With multiple notes, both aliases are listed ok as being played 
# - Confirmed that it DOES play the one note, even when it's not being listed 
#   -> This might just be because an initial play trigger happens on 0.0 
#   -> Confirmed: The 0.0 trigger does not have a logout 
# - Conclusion: Probably a master arg issue, sequencer is probably fine 

# Changing [] to :: for the first one seems to corrupt the second, making their time args the same as the first one
# This error does not happen if the first one has more than one note 
# Added a test that confirms this behaviour. Suspecting a race condition due to shared state, but cannot for the life of me get it to reveal itself in printing


#Synth("M8 5 5 8 5 5 8 5 5 6 9 13 :: =0.25 #0.2 >0.1 relT0", "########################################### BAMBOO").play("brute")
#Synth("M2 4 :: =1.2 #0.8 >0.4 relT0.2 lfoS222 lfoD0.5", "arg2").play("gentle")

# Feb/Mar 2023 notes 
# - c4 syntax is doable but relies on what we do OUTSIDE of parsing since parsing only creates MSG objects 
#   - Idea is that you can take the prefix and index and work around those 
# - Master arg syntax ::; is not clear on behaviour. Does it multiply, replace or something else? Is there another? 
# - Lots of things happen here in this file that need their own testing 
#   - Just the fact that testing provides examples is very helpful
#   - We need a new class for playing around so this one can be for testing 
# - Generally: This library and a bootup-script is the main focus atm
#   - Idea is to create a solid foundation. It's hard to keep working unless the smallest pieces are truly plug and play
#   - Minor changes to jdw-sc might come in handy too, like tweaking the delay and streamlining default args 
#   - Could maybe use another drum machine as well 
# - BIG ONE: Starting works just fine, but muting and then restarting is a bother. Make jdw-sequencer completely delete muted tracks. 
#   -> This would make the next populated send behave as if starting a new track, which is what we want anyway 
#       UPDATE: DONE 
# - Master args appear to break (/) syntax 
#   -> Haven't found an example yet, need to explore this - might just be a bug with ::; 

