### Earlier notes from PROSC

# Placing in order doesn't solve the original problem of wanting to know which kind of sample 
# to expect when writing a certain note number 
# On the other hand, reserving chunks of tones for certain sample families might also backfire
# both in terms of varying amounts of files available and in terms of piano roll bloat
# If we included "family" and "family index" in sample data we could make a whole new API for sample 
# plays. 

# "bd1[#5] hh12 sd1 tm44 sh1 cy1 be1 mi1"
# The problem then becomes reuse. We can rather easily extract the sheet parsing and replace the digits-first
# rule with some kind of pre-tag scanner.
# After that we just implement another endpoint; the sequencer doesn't care. 
# One more reuse-problem is other sheet and metasheet functionality. 
# - We are overdue for a general refactor. 
#   - Separating "freq"-kind messages from "tone/index"-kind messages at creation
#       - Different "sheet" functions in meta-sheet? 
#   - Consistent, immutable arg names that need no post-processing for sending
#       - See _export_note and sheet.to_notes
#   - All forms of sheet parsing separated into a lib 
#
#
# MIDI_EVENT: {"target": "nintendo", "type": "NOTE_ON", "args": [...]}
# SAMPLE_PLAY: {"target": "dr660", "family": "BASS(0)", "index": 4, "args": {...}}
# S_NEW: {"target": "moog", "args": {...}}

# A starting point could be to just include the pre-tag with everything else and then 
# have separate export methods for all notes still. 
# It might be a good idea to start enforcing objects instead of dict[dict] stuff

### Structural plan 

# Classes 
1. "Sheet" equivalent that handles parsing, tagging and other uniform "note" procedures
2. "MetaSheet" equivalent that handles orchestration of multiple sheets 
3. "Exporter" class to be passed into MetaSheet, containing any logic needed to actually handle the notes 
    - This would include "to_hz", transposing, posting type, all that 
4. "SheetNote" class as it comes out of sheet parsing:
    - "prefix": only used for sampling 
    - "suffix": "tags" as we call them now 
    - "tone_value": float to allow both manual freq and midi_tone
    - "master_args": As parsed by the [] box to ensure they are not overwritten
    - "base_args": "args" as we call them now 