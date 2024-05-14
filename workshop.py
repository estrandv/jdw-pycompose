import songs.example as song

"""

======================
FEATURE BRAINSTORM ===
======================

# Break handling 

- "Play this every x loops, but still treat each loop as a valid entry point for other tracks"
    -> A step towards this is letting sequencer.queue be a VECTOR, which you can then later apply logic to.
        An index per sequencer and a modulo is enough to eat through it on each requeue. 
    -> This feature is more general and "nice-to-have"
- "Play this break on the next switch, then go back to what you're playing right now"
    -> This is the equivalent of calling queue, waiting for requeue, then calling again with the old queue 
    -> Binding certain breaks to special key combinations is one way to do it, but ultimately it's more of a 
        sequencer feature than a pycompose one. 
    -> Vector queues don't automatically solve this either, since they are implied as ever-looping.
    -> If each list of notes in the vector also has a ONE_OFF or REPEAT setting, this works somewhat well.
        This would however come with a lot of implications, not least for the ONE_OFF method we use today
        to mute unmentioned tracks. 
    - How it works today: 
        - Each sequencer has a "wipe_on_finish" setting, which removes the whole sequencer completely 
            - This allows START_MODE to apply when it is re-queued later (although adding them to INACTIVE would work too)
            - The easiest adaptation is to only wipe once ALL queues are finished, or once the queue is empty
                - ON_QUEUE_EMPTY(WIPE / STALL)?   
        - Starts and resets verify modes, which I guess would go for the current active sequence regardless of queue being a vector

    - Notable, about vector queues as a solution to this: 
        - If we queue <break> and then want to go back to <regular> today, we have only the time of the <break> to requeue <regular>
        - If we use vector queues, even without one-shot, we instead have the full run of <break> AND <regular> to requeue only <regular>
            - So there is some gain immediately 

"""


# TODO: Rename workshop.py and anything referencing it 
song.run()