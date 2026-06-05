# jdw-pycompose

Song composition and orchestration layer for the JackDAW system. Compiles Billboard (`.bbd`) files into OSC commands that drive the sequencer, SuperCollider, and sampler subsystems.

## What It Does

- Reads `.bbd` song files using `jdw-billboarding-lib`
- Compiles template synths into SuperCollider `SynthDef` code using `compile_scd.py`
- Loads sample packs and synthdefs onto the server
- Manages live queue updates to the sequencer (note-on, note-off, parameter changes)
- Supports non-real-time (NRT) recording for offline rendering
- Provides a template/macro language via `macros.py` for code generation within billboard files

## Usage

```bash
~/mypython/bin/python run.py --setup path/to/song.bbd    # Load synthdefs, samples, config
~/mypython/bin/python run.py --update path/to/song.bbd    # Send queue updates live
~/mypython/bin/python run.py --stop                       # Stop all sequences
~/mypython/bin/python run.py --nrt path/to/song.bbd out   # NRT render to file
```

## Key Concepts

- `@synth_name:args` sections define which synth to use for subsequent shuttle-notation tracks
- `SP_` prefix selects sample pack mode (sampler synth)
- `DR_` prefix selects drone mode (single sustained synth instance, uses note_mod)
- `>>> filters` define which sections/groups play (live uses latest; NRT composes in order)
- `template_synths.txt` compiles to SuperCollider SynthDefs, reducing boilerplate

## Dependencies

- `jdw-billboarding-lib` — billboard file parsing
- `python-osc` — OSC client for sending commands
- `natsort` — natural sorting for file ordering

## Songs

Song `.bbd` files live in the `songs/` directory.
