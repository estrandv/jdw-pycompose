# WIP all-in-one calls to JDW via new billboard


from time import sleep
from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_message import OscMessage
from pythonosc.udp_client import SimpleUDPClient
from billboard_osc_conversion import get_all_command_messages, get_all_effects_create, get_all_effects_mod, get_sampler_keyboard_config, get_sequencer_batch_queue_bundle, get_synth_keyboard_config
from billboarding import parse_billboard

from billboarding import Billboard
from default_configuration import get_default_samples, get_default_synthdefs, get_effects_clear
from billboarding import CommandContext
import temp_import.default_synthdefs as default_synthdefs
import temp_import.sample_reading as sample_reading

def default_client() -> SimpleUDPClient:
    return SimpleUDPClient("127.0.0.1", 13339) # Router

# One-time stups like loading all default synths (many messages, time-intensive)
def setup(bdd_path: str):
    client = default_client()

    with open(bdd_path, 'r') as bdd_file:
        billboard: Billboard = parse_billboard(bdd_file.read())

        all_messages: list[OscMessage] = [sample.load_msg for sample in get_default_samples()] + [synth.load_msg for synth in get_default_synthdefs()]

        for msg in all_messages:
            sleep(0.005) # Seems to be needed to prevent dropped messages. This is a tested minimum for 100% configure.
            client.send(msg)

def configure(bdd_path: str):
    client = default_client()


    with open(bdd_path, 'r') as bdd_file:
        billboard: Billboard = parse_billboard(bdd_file.read())

        all_messages: list[OscMessage] = []

        all_messages += get_sampler_keyboard_config(billboard)
        all_messages += get_synth_keyboard_config(billboard)

        all_messages += [get_effects_clear()]
        all_messages += get_all_command_messages(billboard, [CommandContext.ALL, CommandContext.UPDATE])
        all_messages += get_all_effects_create(billboard)

        for msg in all_messages:
            sleep(0.005) # Seems to be needed to prevent dropped messages. This is a tested minimum for 100% configure.
            client.send(msg)

def nrt_record(bdd_path: str):
    client = default_client()
    with open(bdd_path, 'r') as bdd_file:
        billboard: Billboard = parse_billboard(bdd_file.read())

        """
        TODO: NRT STEPS
        - Requirement: Must not pre-filter anything with groups
            => Billboard just retains them so I think this is ok!
        - Requirement: Must time-osc all setup messages as 0.0, with the rest as normal
        - Requirement: Must filter according to:
            - Only load synthdefs that:
                - Equal the master instrument (or sampler if sampler) OR
                    => UPDATE: Added header to BillBoardSynthSection; now we know instrument_name and is_sampler
                - Equal one of the track-provided effects (BillBoardTrack has EffectMessage which has instrument_name)
            - Only load samples that/when:
                - (easy) using sampler
                - (easy) are part of the sample pack
                - (hard) are referenced by a track
            - Only load routers referenced by a track
        - Requirement: Must create timeline
            - Needed to represent the whole repeating structure
            - Uses the SCORE class from nrt_scoring
                - Which should be modified to use as raw classes as possible (so list of elements instead of direct track references)
        - Requirement: Must reuse as much as possible
            - Today, track osc is determined in parsing.process_synth_section
            - This is present in parse_billboard from billboarding, so the final result is workable
            - Only in get_sequencer_batch_queue_bundle is time added, so we can easily dodge that and create our own
            - Scoring fetches time independently, but if it were to use ElementMessage it could resolve it as written there

        => Conclusion: Full Billboard can be used as starting data

        => Starting point: Rewrite of scoring using ElementMessage (remember: relative times are not needed)
            - According to above: fetch time straight from ElementMessage definition; use BigDecimal conversion for timekeeping
            - Note: output can still be raw elementMessage; time is only needed in scoring to know how long the tracks are
                - So we can use an internal timed class but still export ElementMessage

                => UPDATE: Made an NRT scoring model that allows us to export the finished tracks as pure timed osc, accounting for silence
                    -> Next up is to just use that to construct an nrt message the normal way (walk through flters and extend)
        => Then: All 0.0 messages can just be fetched and appended at start with a 0.0 timewrap (create_timed)



        """


def update_queue(bdd_path: str):
    client = default_client()

    with open(bdd_path, 'r') as bdd_file:
        billboard: Billboard = parse_billboard(bdd_file.read())

        all_messages: list[OscMessage | OscBundle] = []

        # Keyboard is configured on regular run as well
        all_messages += get_synth_keyboard_config(billboard)
        all_messages += get_sampler_keyboard_config(billboard)

        # TODO: effects mod seems to behave a bit weirdly - might be because new method fails to give them unique ids if they dont have a group
        #   - UPDATE: Yes. I think regex might actually grab "effect_a_" as a match for all with e.g. "effect_a_mygroup". This is a bit unintuitive but not really a bug...
        # TODO: Split default synths by ";" instead and just make it an scd file for proper highlighting
        # TODO: Default synths and sample config should both be neat files like the bbd to allow them to live in another repo
        # TODO: In the future, we might want to be able to specify sample loading in bbd
        all_messages += get_all_command_messages(billboard, [CommandContext.ALL, CommandContext.QUEUE])
        all_messages += get_all_effects_mod(billboard)
        all_messages += [get_sequencer_batch_queue_bundle(billboard)]

        for msg in all_messages:
            sleep(0.005) # Seems to be needed to prevent dropped messages
            client.send(msg)

example = "/home/estrandv/programming/jdw-pycompose/songs/courtRide.bbd"
setup(example)
configure(example)
update_queue(example)
