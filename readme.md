# JAM Library for JDW 
- Uses "billboard" .bbd files to compile songs using jdw-billboarding-lib
- See run.py for available run commands 

### Quick concepts 

- "@" sections denote which synthdef and args to use for any shuttle-notation tracks defined below 
    - "SP_" prefix denotes using a sample pack 
    - "DR_" prefix denotes using monophonic "drone mode" for the tracks
        - Essentially: Create a single instance of the synth and use note_mod instead of note_on for all track notes
        - Also has a bunch of other hacks in order to behave seamlessly 
- ">>>" defines filters for which sections/groups to play
    - Live: Use latest defined filter
    - NRT: Compose song in order of filters
- template_synths.txt gets compiled to Supercollider-compatible synthdefs (circumventing common boilerplate) 