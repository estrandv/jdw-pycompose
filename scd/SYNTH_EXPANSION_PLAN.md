# SynthDef Expansion Plan

## Priority Order

1. **Bass** (at least 5 new, varied defs) — see section 5a
2. **Subtractive** and **Additive** synths
3. **Effects** (phaser, flanger, chorus, bitcrush, limiter)
4. Low/no-priority: physical modeling (separate sampler), pads, organs (adequate already)

## Efficiency Notes (gathered during workflow development)

These findings are critical for fast agent iteration:

### NRT Pipeline
- `sclang` **must** have stdin closed (`stdin=subprocess.DEVNULL` in Python,
  or `< /dev/null` in shell) — otherwise it enters REPL mode and never exits.
- Use `SynthDef.new("name", {...}).load` to write the binary `.scsyndef` to
  the standard synthdef directory (`~/.local/share/SuperCollider/synthdefs/`).
- Render command: `scsynth -o 2 -N <score.osc> <silent.wav> <output.wav> 44100 WAV int16`
- Clean up the synthdef directory between runs to avoid stale defs.

### SynthDef Extraction (Python)
- Brace-matching is required to extract full SynthDef blocks — naive regex (non-greedy
  `.*?`) fails on any synth with nested `{}` (e.g., `Env.adsr` arguments).
- Appending `.load` is simpler than parsing brace positions: just strip trailing
  `;` or whitespace from the extracted block and add `.load;`.

### WAV Analysis
- **Zero-crossing frequency estimation is unreliable for complex waveforms.**
  Only use it as a warning, not a PASS/FAIL criterion. Skip trailing silence.
- **RMS < 1** reliably indicates silence (failed doneAction or envelope).
- **DC offset > 200** (in 16-bit) indicates waveshaping/filter issues — suggest LeakDC.
- **Peak > 32000** indicates clipping — reduce internal gain staging.

### Known Limitations
- Effects (router, delay, reverb, compressor, etc.) are **silent without input routing**
  and must be skipped in batch tests.
- Some UGens require sc3-plugins or supercollider-portedplugins (e.g., AnalogChew,
  AnalogTape). Check availability before testing.
- The `ksBass` synth has a genuine DC offset issue (~700 in 16-bit) — it needs LeakDC.

### SC Language Gotchas (SynthDef context)
- `Env` release curves: a **positive curve** value (e.g., 4) creates a slow-start / fast-end
  shape — the envelope holds high then snaps silent at the end, causing an audible click.
  Always use **negative curves** (e.g., -4) for release segments to get exponential decay
  (fast-start / slow-end, smooth fade to silence), or 0 for linear.
- `Mix.fill(n, func)` requires `n` to be a **compile-time integer literal**, not a synth
  control parameter (OutputProxy). Use a fixed number or unroll the fill.
- `Env` curve parameters (the `curve` axis in `Env.new`/`Env.adsr`) must be **literal
  values**, not synth control params. They determine the mathematical segment shape at
  compile time. However, `Env` `levels` and `times` CAN be control params.
- `DelayC`, `Ringz`, and other filter-based UGens can produce significant gain boost
  (3-20 dB) near resonance — watch for **clipping** in the signal chain. Use `Limiter.ar`
  as a safety net, or reduce upstream mix levels.
- Use `LeakDC.ar` after any waveshaping, filter, or modulation that might introduce
  DC offset (e.g., `distort`, `clip`, unbalanced modulation).

## Overview

This document is a self-contained plan for expanding the SuperCollider SynthDef
library in `jdw-pycompose/scd/synthDefs.scd`. It describes:

1. The context and conventions of existing synthdefs
2. How to generate WAV audio using SC's NRT (Non-Real-Time) mode
3. How to programmatically analyze WAV output for correctness
4. Categories of new synths to create, with specific ideas
5. A test harness workflow for iterative development

An agent can follow this document alone to add new, verified synthdefs.

---

## 1. Context — Existing SynthDefs

**File**: `jdw-pycompose/scd/synthDefs.scd` (585 lines)

### Conventions

Each SynthDef follows this pattern:

```supercollider
SynthDef.new("name", {|amp=1, freq=440, gate=1, out=0, pan=0,
    // synth-specific params with defaults
    var osc, env, ...;

    // 1. freq handling (lag, detune, fmod)

    // 2. Oscillator(s)

    // 3. Envelope (Env.adsr / Env.asr / Env.perc / Env.new)
    //    Must include doneAction: Done.freeSelf or DetectSilence

    // 4. Mix, Pan2, Out
    osc = Mix(osc) * 0.5;
    osc = Pan2.ar(osc, pan);
    Out.ar(out, osc)
})
```

### Existing Synths

| Name | Type | Key Features |
|------|------|-------------|
| experimental | Saw/VarSaw | dual detuned saws, ADSR, pan |
| eBass | Bass | saw wave, envelope filter, waveshaper, shelves |
| organReed | Organ | Pulse w/ rand freq jitter, latch grit, BPF/BHiShelf |
| pluck | Pluck | twin sine+VarSaw phase, XLine decay |
| blip | Blip/Pluck | LFCub+LFTri, Blip ring modulation, XLine |
| karp | Karplus-Strong | noise burst + CombL delay |
| arpy | Arp/Seq | Impulse into LPF, perc envelope |
| prophet | Synth | detuned Pulse, LFO PWM, RLPF+BHiPass |
| jbass | Bass | LFTri, sin-curve envelope |
| ksBass | KS Bass | shaped impulse + CombN, RLPF + Compander |
| dBass | Bass | VarSaw w/ frequency glide, LFO width |
| gritBass | Bass | LFPar sub-octave trick (phase flip) |
| oc2bass | Bass | LFPar octave-down (mirror trick) |
| feedbackPad | Pad | LFTri + LocalIn feedback, quantized pitch, LPF bank |
| aPad | Pad | dual SinOsc, vibrato + tremolo, distort |
| moogBass | Bass | VarSaw detune, MoogFF, S&H chorus |
| samplerALT | Sampler | PlayBuf w/ envelope, rate control |

### Effects

| Name | Type | Notes |
|------|------|-------|
| router | Utility | Thru |
| clamp | Filter | HPF+LPF with modulatable cutoff |
| delay | Delay | CombL |
| controlMod | Utility | Lagged kr output |
| compressor | Dynamics | Compander |
| tube | Distortion | Stub (TODO) |
| distortion | Distortion | clip+fold2 |
| analogTape | Saturation | AnalogTape UGen |
| analogChew | Distortion | AnalogChew UGen |
| reverb | Reverb | FreeVerb |
| vverb | Reverb | Allpass diffusion network |

### Parameter Naming

- Standard: `amp, freq, gate, out, pan`
- Envelope: `attT, decT, susL, relT, susT`, or `att, decay, rel` if taken (legacy convention)
- Legacy generic: `fxi, fxii, fxiii, ..., fxxii` (mapped to various params) (avoid)
- Modern descriptive: `cut, rq, drive, blend, room, mix` (good for unique properties, but keep names short)

### Important Gotchas

- `freq` is often wrapped in `[freq, freq+fmod]` for stereo detune — common style
- `amp` is sometimes scaled inside the def (e.g., `amp * 0.1`)
- Envelopes use either `Done.freeSelf` or `DetectSilence` for cleanup
- `Done.freeSelf` requires `gate` to function (gate=0 triggers release)
- `Mix(osc) * 0.5` is the standard mix-down pattern

---

## 2. NRT Rendering Pipeline

SuperCollider can render WAV files without a real-time audio server using its
NRT (Non-Real-Time) mode. The pipeline has two steps:

### Step 1: Prepare (via `sclang`)

A SuperCollider script generates:
- A binary synthdef file (`.scsyndef`)
- An OSC score file (`.osc`) containing note-on/note-off commands

```supercollider
// prepare.scd
// Write the compiled SynthDef binary to disk
SynthDef(\mySynth, {
    // ... definition ...
}).writeDefFile("/path/to/output/dir".standardizePath);

// Write the OSC score as a sequence of timed events
Score([
    [0.0, [\s_new, \mySynth, 1000, 0, 1, \freq, 440, \amp, 0.5]],
    [0.5, [\n_set, 1000, \gate, 0]],
]).write("/path/to/output/score.osc".standardizePath);

0.exit;
```

Run it:
```bash
sclang /path/to/prepare.scd < /dev/null
```

The `< /dev/null` is critical — without it `sclang` stays in REPL mode and
never exits. The script exits via `0.exit;`.

**Output files**:
- `mySynth.scsyndef` — compiled UGen graph binary
- `score.osc` — OSC command sequence

### Step 2: Render (via `scsynth`)

`scsynth -N` reads the OSC score and writes an audio file:

```bash
scsynth -o 2 -N <score.osc> <input.wav> <output.wav> <sr> <header> <sample_format>
```

Arguments:
- `-o 2` — stereo output (omit for 8-channel default)
- `<score.osc>` — the OSC command file from step 1
- `<input.wav>` — dummy input file (required even for pure synthesis)
- `<output.wav>` — the rendered audio
- `<sr>` — sample rate (e.g., 44100)
- `<header>` — file format (e.g., `WAV`, `AIFF`)
- `<sample_format>` — bit depth (e.g., `int16`, `int24`, `float`)

Example:
```bash
scsynth -o 2 -N /tmp/score.osc /tmp/silent.wav /tmp/output.wav 44100 WAV int16
```

### Generating the Silent Input

The dummy input WAV must match the expected channel count. Use Python:

```python
import wave, struct
with wave.open('/tmp/silent.wav', 'w') as w:
    w.setnchannels(2)
    w.setsampwidth(2)       # 16-bit
    w.setframerate(44100)
    w.writeframes(struct.pack('<' + 'h' * 88200, *[0] * 88200))  # 1 second silence
```

Or with sox:
```bash
sox -n /tmp/silent.wav rate 44100 channels 2 trim 0 1
```

### Synthdef Path

`sclang` writes `.scsyndef` files to the directory specified in
`writeDefFile()`. When running `scsynth`, these files must be on the synthdef
search path (typically `~/.local/share/SuperCollider/synthdefs/`). Either:

- Write directly to that path, or
- Copy the `.scsyndef` file there before running `scsynth`

The default path can be found at runtime:
```supercollider
SynthDef.synthDefDir  // returns path string
```

### Score Format

The Score is a list of `[time, [command, ...]]` entries:

```supercollider
Score([
    // [time, [\s_new, synthName, nodeID, addAction, targetID, ...params]]
    [0.0, [\s_new, \mySynth, 1000, 0, 1, \freq, 440, \amp, 0.5]],
    // [time, [\n_set, nodeID, \param, value, ...]]
    [0.5, [\n_set, 1000, \gate, 0]],
    // [time, [\n_free, nodeID]]
    [1.0, [\n_free, 1000]],
])
```

Node IDs must be unique. AddAction 0 = head of group, targetID 1 = default group.

---

## 3. WAV Analysis (Programmatic Testing)

After rendering, analyze the WAV to verify correctness. Tools available:
- `sox` and `sox <file> -n stats` — statistics (peak, RMS, DC offset)
- `ffprobe` — metadata (duration, channels, format)
- Python `wave` module (stdlib) — full programmatic access
- Python `struct` — sample unpacking

### Sanity Checks

#### A. Compilation Check
If `sclang` or `scsynth` exits with non-zero, the synthdef has errors.
Parse stderr for "ERROR" or "FAILURE".

#### B. Silence Detection
If all samples are near-zero, the synth produced no audible output.
Likely causes: wrong doneAction, envelope not opening, wrong freq (e.g., 0 Hz).

```python
samples = [...]  # unpacked
rms = (sum(s**2 for s in samples) / len(samples)) ** 0.5
if rms < 1:  # 16-bit: RMS < 1 means essentially silent
    print("WARNING: Synthesizer produced silence")
```

#### C. Clipping / Distortion
Peak values at exactly ±32767 (int16) or very close indicate clipping.
This means gain staging is wrong (amp too high, or internal signal > 1.0).

```python
max_val = max(abs(s) for s in samples)
if max_val > 32000:
    print(f"WARNING: Possible clipping, peak = {max_val}")
```

#### D. DC Offset
If the mean of all samples is significantly non-zero:
```python
dc = sum(samples) / len(samples)
if abs(dc) > 100:  # ~0.3% of full range
    print(f"WARNING: DC offset detected: {dc}")
```

#### E. Frequency / Pitch Check
Count zero crossings to estimate fundamental frequency:
```python
zc = sum(1 for i in range(1, len(samples))
         if (samples[i] >= 0) != (samples[i-1] >= 0))
freq_est = (zc / len(samples)) * sr / 2
if abs(freq_est - expected_freq) > expected_freq * 0.05:
    print(f"WARNING: Freq mismatch: expected {expected_freq}, got {freq_est}")
```

#### F. Duration Check
If rendered duration differs significantly from expected:
- Check envelope times
- Check doneAction firing too early

#### G. Stereo Balance
Compare L and R channel RMS; large imbalance may indicate panning issues.

#### H. Envelope Shape (for percussive synths)
Check the amplitude envelope shape: for a percussive sound, the
peak should occur early and decay. Plot or check peak position.

### Analysis Script Template

```python
import wave, struct, sys

wav = wave.open(sys.argv[1], 'r')
sr = wav.getframerate()
frames = wav.readframes(wav.getnframes())
channels = wav.getnchannels()
samples = struct.unpack('<' + 'h' * (len(frames)//2), frames)

# Per-channel analysis
for ch in range(channels):
    ch_samples = samples[ch::channels]
    rms = (sum(s**2 for s in ch_samples) / len(ch_samples)) ** 0.5
    peak = max(abs(s) for s in ch_samples)
    dc = sum(ch_samples) / len(ch_samples)
    zc = sum(1 for i in range(1, len(ch_samples))
             if (ch_samples[i] >= 0) != (ch_samples[i-1] >= 0))
    freq_est = (zc / len(ch_samples)) * sr / 2

    print(f"Ch{ch}: RMS={rms:.1f} Peak={peak} DC={dc:.2f} "
          f"FreqEst={freq_est:.1f}Hz")
```

---

## 4. Progress

### Batch 1 — Bass (Priority 1) — 6 synths, all PASS & auditioned
- `fmBass`, `acidBass`, `reeseBass`, `subBass`, `pluckBass`, `analogBass`
- All under `scd/new_synths/`

### Batch 2 — Subtractive + Additive (Priority 2) — 4 synths, all PASS
- `syncLead` — hard-synced SyncSaw lead
- `stringMachine` — Solina detuned saws + BBD chorus
- `pwmPad` — 3 detuned pulses with LFO PWM
- `additivePad` — 8-harmonic sine additive pad

### Next: Effects (Priority 3) — phaser, flanger, chorus, bitcrush, limiter

---

## 5. Test Harness (Automated Pipeline)

When adding new synths, run them through this pipeline:

### Single Synth Test Script

Place in `scd/test_synth.py`:

```python
#!/usr/bin/env python3
"""Test a single SynthDef by rendering it via NRT and analyzing the output."""
import argparse, subprocess, sys, os, tempfile, wave, struct, math

SCD_DIR = os.path.dirname(os.path.abspath(__file__))
SYNTHDEF_DIR = os.path.expanduser("~/.local/share/SuperCollider/synthdefs/")

def make_silent_wav(path, dur=2.0, channels=2, sr=44100):
    with wave.open(path, 'w') as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(b'\x00\x00' * sr * dur * channels)

def analyze_wav(path, expected_freq=None):
    wav = wave.open(path, 'r')
    sr = wav.getframerate()
    channels = wav.getnchannels()
    frames = wav.getnframes()
    data = wav.readframes(frames)
    samples = struct.unpack('<' + 'h' * (len(data)//2), data)
    dur = frames / sr
    print(f"  Duration: {dur:.3f}s, Channels: {channels}, SR: {sr}")
    issues = []
    for ch in range(channels):
        ch_s = samples[ch::channels]
        rms = (sum(s**2 for s in ch_s) / len(ch_s)) ** 0.5
        peak = max(abs(s) for s in ch_s)
        dc = sum(ch_s) / len(ch_s)
        zc = sum(1 for i in range(1, len(ch_s))
                 if (ch_s[i] >= 0) != (ch_s[i-1] >= 0))
        freq_est = (zc / len(ch_s)) * sr / 2
        print(f"  Ch{ch}: RMS={rms:.1f} Peak={peak} DC={dc:.2f} FreqEst={freq_est:.1f}Hz")
        if rms < 1: issues.append("SILENCE")
        if peak > 32000: issues.append("CLIPPING")
        if abs(dc) > 100: issues.append(f"DC_OFFSET({dc:.1f})")
        if expected_freq and abs(freq_est - expected_freq) > expected_freq * 0.05:
            issues.append(f"FREQ_MISMATCH(expected={expected_freq},got={freq_est:.0f})")
    if issues:
        print(f"  ISSUES: {', '.join(issues)}")
        return False
    print("  OK")
    return True

def render_synthdef(scd_file, synth_name, params, dur=1.0):
    """Render a synthdef via NRT and return path to WAV."""
    tmp = tempfile.mkdtemp()
    silent = os.path.join(tmp, "silent.wav")
    make_silent_wav(silent)
    score_path = os.path.join(tmp, "score.osc")
    wav_path = os.path.join(tmp, "output.wav")

    # Build the sclang script
    sc_script = f'''
SynthDef(\\{synth_name}, {scd_content if ...}).writeDefFile("{tmp}".standardizePath);
Score([
    [0.0, [\\s_new, \\{synth_name}, 1000, 0, 1, {_params_to_sc(params)}]],
    [{dur}, [\\n_set, 1000, \\gate, 0]],
]).write("{score_path}".standardizePath);
0.exit;
'''
    # ... run sclang, then scsynth ...
    return wav_path
```

### Automated Test Flow

```
For each new synthdef:
  1. Write the SynthDef as a separate .scd file in scd/new_synths/
  2. Run test script: python3 scd/test_synth.py scd/new_synths/mySynth.scd
     - Renders at C4 (262 Hz) and C3 (131 Hz)
     - Analyzes output
     - Reports PASS/FAIL with reasons
  3. On PASS: append to synthDefs.scd (or keep as separate file)
  4. On FAIL: fix issues, re-render, re-analyze
```

---

## 5a. Bass Synths (Priority 1)

Six new basses have been implemented and verified:

| Name | Type | Character | Key Features |
|------|------|-----------|-------------|
| `fmBass` | FM bass | DX-style punchy transient | 2-operator FM, pitch env, index decay |
| `acidBass` | 303-style | Squelchy resonant | Saw/square, MoogFF envelope follower, accent |
| `reeseBass` | Detuned saws | Massive, moving | 5 detuned saws, chorus comb filtering |
| `subBass` | Clean sub | Deep/minimal | Sine + square blend, ultra-simple |
| `pluckBass` | Electric bass | Wooden, warm | Triangle harmonics, Ringz body resonance, Limiter |
| `analogBass` | Minimoog | Classic analogue | 3 osc (2 saws + pulse), Moog ladder filter, drive |

All pass the test harness at 65Hz, 131Hz, and 262Hz.

**Human-verified:** All six sound good. FM, Reese, and analog basses were called out as
particularly successful. The NRT analysis pipeline caught real issues (clipping, DC offset,
compile errors) that would have sounded bad; human audition confirmed the remaining synths
are musically useful. Workflow validated.

## 5b. Synth Categories to Add (Future)

### FM Synthesis (next priority after subtractive/additive)
- `fmBell` — 2-operator FM, percussive env
- `fmBass` — 2-operator, low ratio, pitch env
- `fmEPiano` — 4-operator style (FM + feedback)
- `fmPad` — 2-op with slow mod env
- `fmBrass` — mod index follows envelope

### Additive
- `additivePad` — bank of SinOsc with harmonic spread, slow mod
- `additiveOrgan` — drawbar-style sine bank
- `formantVox` — formant filter bank (vowel shapes)

### Subtractive
- `ladderBass` — Moog-style 4-pole with resonance
- `stringMachine` — saw detune + ensemble chorus
- `syncLead` — hard-synced saws, filter sweep
- `pwmPad` — Pulse width modulation, multi-voice detune
- `wobbleBass` — LFO filter sweep, saw core

### Physical Modeling
- `marimba` — noise burst into bank of resonators
- `snareDrum` — filtered noise + tone component
- `kickDrum` — sine + click, pitch envelope
- `hihat` — HPF noise, short env
- `bowedString` — self-oscillating delay + bow noise
- `flute` — noise + resonant filter with feedback
- `pluckedString` — KS with dynamics, pickup position

### Granular
- `cloudPad` — GrainBuf with position jitter
- `grainFlute` — GrainSin with freq jitter

### Chaos / Generative
- `lorenzPad` — Lorenz system oscillators
- `feedbackBass` — recursive delay network

### Effects (more needed)
- `phaser` — allpass chain with LFO
- `flanger` — comb filter with LFO
- `chorus` — modulated delays
- `bitcrush` — sample rate + bit depth reduction
- `stereoWidth` — M/S widening
- `eq` — simple shelving/peak filters
- `limiter` — soft clip / lookahead

---

## 6. Batch Testing Strategy

Rather than run each synth manually, a batch script can:

1. Scan `scd/new_synths/*.scd` for files starting with `SynthDef.new(`
2. Parse the SynthDef name and parameters
3. Run each through the full NRT pipeline at C3, C4, C5
4. Generate a summary table:

```
Synth        | C3 (131Hz) | C4 (262Hz) | C5 (523Hz) | Issues
-------------|------------|------------|------------|-------
fmBell       | PASS       | PASS       | PASS       |
fmBass       | PASS       | PASS       | PASS       |
additivePad  | SILENCE    | SILENCE    | SILENCE    | Check doneAction
ladderBass   | PASS       | PASS       | CLIPPING   | Reduce amp
```

5. Only synths that PASS all checks are ready for review.

---

## 7. File Organization

```
jdw-pycompose/scd/
├── synthDefs.scd              # Existing synthdefs (keep as-is)
├── SYNTH_EXPANSION_PLAN.md    # This document
├── new_synths/                # New synthdefs (one per .scd file, or batches)
│   ├── fmBell.scd
│   ├── fmBass.scd
│   ├── ladderBass.scd
│   └── ...
├── test_synth.py              # Test harness script
├── batch_test.py              # Batch testing script
├── nrt_helpers/               # Helper files
│   ├── prepare.scd.template   # Template for sclang preparation script
│   └── silent.wav             # Pre-generated silent input
└── wav_outputs/               # Rendered test WAVs (gitignored)
```

---

## 8. Adding a New Synth — Step-by-Step

1. **Create the .scd file**: `scd/new_synths/mySynth.scd`
   - Follow existing conventions (params, env, Pan2, Out)
   - Document what the synth is supposed to sound like

2. **Run the test harness**:
```bash
python3 scd/test_synth.py scd/new_synths/mySynth.scd
```
This renders and analyzes at default pitch (262Hz).

Test multiple frequencies:
```bash
python3 scd/test_synth.py scd/new_synths/mySynth.scd --freq 131 262 523
```

Batch test an entire directory:
```bash
python3 scd/batch_test.py scd/new_synths/
```

The batch script skips known-broken synths (effects, missing UGens) and
produces a summary table.

3. **Review analysis output**:
   - `SILENCE` → Fix doneAction or envelope logic (envelope never opens)
   - `CLIPPING` → Reduce internal gain/amp (signal > 1.0 somewhere)
   - `DC_OFFSET` → Add LeakDC or fix waveshaping
   - `FREQ_MISMATCH` → Warning only (zero-crossing estimator is unreliable
     for complex/harmonic waveforms). Only meaningful for pure sine waves.
   - `SCLANG_TIMEOUT` → SynthDef has a compilation error, usually a missing
     UGen or syntax error that triggers SC's debugger on error.

4. **Iterate** until it passes all checks.

5. **Manual listen**: Ask a human to listen and confirm the timbre
   is musically useful. Adjust parameters as needed.

6. **Finalize**: Add the new SynthDef to `synthDefs.scd` following
   existing style conventions.

---

## 9. Known-Broken Synths (in existing synthDefs.scd)

Some synths in the existing file depend on external UGens or require audio
input routing and will fail the test harness. These are skipped by
`batch_test.py`:

| Synth | Reason |
|-------|--------|
| samplerALT | Needs buffer input |
| router | Effect — needs audio input |
| clamp | Effect — needs audio input |
| delay | Effect — needs audio input |
| controlMod | Control-rate only (no audio output) |
| compressor | Effect — needs audio input |
| tube | Stub (TODO implementation) |
| distortion | Effect — needs audio input |
| analogTape | Effect — needs audio input |
| analogChew | Missing UGen (sc3-plugins not installed) |
| reverb | Effect — needs audio input |
| vverb | Effect — needs audio input |

## 10. Test Harness Reference

### `test_synth.py`

Core test script. For each SynthDef:
1. Extracts the definition from the .scd file (brace-matched)
2. Appends `.load` to write the compiled binary to the standard path
3. Creates an OSC score with note on/off at specified freq/amp/dur
4. Runs `sclang` to compile and write binary + score
5. Runs `scsynth -N` to render the WAV
6. Analyzes the WAV for: RMS, peak, DC offset, zero-crossing frequency

Usage:
```
test_synth.py <files...> [--synth NAME] [--freq HZ [HZ...]]
                [--dur SEC] [--amp AMP]
```

### `batch_test.py`

Scans .scd files, runs each synth through test_synth.py at multiple
frequencies, and prints a summary table. Skips known-broken synths.

Usage:
```
batch_test.py [paths...] [--freq HZ [HZ...]] [--dur SEC]
```
