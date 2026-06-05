# AGENTS.md — jdw-pycompose

## Source Structure

```
run.py                 # CLI entry point (--update/--stop/--setup/--nrt)
billboard_running.py   # Core orchestration (setup, configure, queue update, NRT)
compile_scd.py         # Template synth compilation to SynthDefs
file_utilities.py      # Sample/synthdef file loading
macros.py              # Template/macro language for .bbd code generation
listener.py            # OSC response listener (for NRT completion)
scd/                   # Base SuperCollider synthdefs
  synthDefs.scd
scd-templating/
  template_synths.txt  # Template synth definitions with {placeholders}
songs/                 # .bbd song files
```

## Billboard Section Types

Each `.bbd` section maps to a `BillboardLineType`:
- `synth_header` — `@SynthName:args` — declares a synth/group
- `track` — shuttle notation content with optional metadata
- `effect_definition` — audio effect with params
- `default_statement` — default arg overrides
- `command` — real-time OSC commands (e.g., `send /stop`)
- `group_filter` — `>>> group1 group2` — section/group routing
- `comment` — ignored lines

## Build/Test

```bash
~/mypython/bin/python -m pytest   # No tests currently
```

## Key Integration Points

- `billboard_running.py` is the main entry — it opens a `python-osc` client, parses the billboard, and sends OSC messages to `osc-router` (port 13339)
- `compile_scd.py` converts shorthand synth templates (synth_name, params, wavetype) to full SuperCollider SynthDef strings
- `macros.py` provides `SEQ()`, `IF()`, `FOR()` macros for generative song patterns

## NRT Flow

1. Parse billboard -> group filters
2. For each filter (in order), send all notes to sequencer
3. Wait for sequencer to finish
4. Record audio via jdw-sc's NRT record feature
5. Mix and export to output file
