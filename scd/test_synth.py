#!/usr/bin/env python3
"""
Test SuperCollider SynthDefs via NRT rendering + WAV analysis.

Usage:
    python3 test_synth.py path/to/synth.scd
    python3 test_synth.py path/to/synth.scd --freq 220 --dur 2.0
    python3 test_synth.py scd/new_synths/*.scd
    python3 test_synth.py synthDefs.scd          # test all in a file
"""

import argparse
import os
import re
import struct
import subprocess
import sys
import tempfile
import time
import wave

SCD_DIR = os.path.dirname(os.path.abspath(__file__))
SYNTHDEF_DIR = os.path.expanduser("~/.local/share/SuperCollider/synthdefs/")
SCLANG = "sclang"
SCSYNTH = "scsynth"


def find_synthdef_names(content):
    names = re.findall(
        r'SynthDef\.(?:new|def)\s*\(\s*["\'](\w+)["\']', content
    )
    return list(dict.fromkeys(names))  # deduplicate, preserve order


def extract_synthdef_block(content, name):
    pattern = rf'SynthDef\.(?:new|def)\s*\(\s*["\']{name}["\']\s*,'
    match = re.search(pattern, content)
    if not match:
        return None
    start = match.start()
    body_start = content.find("{", match.end())
    if body_start == -1:
        return None
    depth = 1
    i = body_start
    while i < len(content) and depth > 0:
        i += 1
        if i >= len(content):
            break
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
    if depth != 0:
        return None
    end = i + 1
    while end < len(content) and content[end] in " \t\n\r;":
        end += 1
    if end < len(content) and content[end] == ")":
        end += 1
    return content[start:end]


def add_load_to_synthdef(block):
    """Append .load to a SynthDef definition block (which ends with ')').

    extract_synthdef_block returns the full SynthDef.new("name", {...})
    expression including the closing paren. We just append .load after it.
    """
    block = block.rstrip("\n; ")
    if not block.endswith(")"):
        return None
    return block + ".load;"


def make_silent_wav(path, dur=2.0, channels=2, sr=44100):
    with wave.open(path, "w") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(sr)
        frame_count = int(sr * dur)
        w.writeframes(b"\x00\x00" * frame_count * channels)


def analyze_wav(path, expected_freq=None, label=""):
    """
    Analyze a WAV file and return (pass, issues_list).
    """
    wav = wave.open(path, "r")
    sr = wav.getframerate()
    channels = wav.getnchannels()
    frames = wav.getnframes()
    data = wav.readframes(frames)
    dur = frames / sr
    samples = struct.unpack("<" + "h" * (len(data) // 2), data)
    wav.close()

    issues = []
    info_lines = [f"  {label}  Duration: {dur:.3f}s  Channels: {channels}  SR: {sr}"]

    for ch in range(min(channels, 2)):
        ch_s = samples[ch::channels]
        if not ch_s:
            continue
        n = len(ch_s)
        rms = (sum(s * s for s in ch_s) / n) ** 0.5
        peak = max(abs(s) for s in ch_s)
        dc = sum(ch_s) / n

        # Frequency estimation from loud portion only (skip silence at ends)
        active_start = next((i for i, s in enumerate(ch_s) if abs(s) > 100), 0)
        active_end = next(
            (len(ch_s) - i for i, s in enumerate(reversed(ch_s)) if abs(s) > 100),
            len(ch_s),
        )
        active = ch_s[active_start : n - active_end] if active_end < n else ch_s
        freq_est_active = 0.0
        if len(active) > sr * 0.05:
            zc = sum(
                1
                for i in range(1, len(active))
                if (active[i] >= 0) != (active[i - 1] >= 0)
            )
            freq_est_active = (zc / len(active)) * sr / 2

        info_lines.append(
            f"    Ch{ch}:  RMS={rms:8.1f}  Peak={peak:6d}  "
            f"DC={dc:+.2f}  FreqEst={freq_est_active:7.1f}Hz"
        )

        if rms < 1:
            issues.append(f"Ch{ch} SILENCE (RMS={rms:.1f})")
        if peak > 32000:
            issues.append(f"Ch{ch} CLIPPING (peak={peak})")
        if abs(dc) > 200:
            issues.append(f"Ch{ch} DC_OFFSET ({dc:.1f})")

        if expected_freq and freq_est_active > 0:
            err = abs(freq_est_active - expected_freq) / expected_freq
            if err > 0.15:
                info_lines.append(
                    f"    WARN: Ch{ch} freq mismatch (expected={expected_freq:.0f}, "
                    f"got={freq_est_active:.0f}, err={err*100:.0f}%%)"
                )

    for line in info_lines:
        print(line)
    return len(issues) == 0, issues


def nrt_render(synthdef_content, tmp_dir, synth_name, test_params):
    """
    Render a SynthDef via NRT. Returns path to WAV.
    Handles .scsyndef cleanup via .load to standard dir.
    """
    freq = test_params.get("freq", 262)
    amp = test_params.get("amp", 0.5)
    dur = test_params.get("dur", 1.0)

    # Build the prepare.scd
    modified = add_load_to_synthdef(synthdef_content)
    if not modified:
        return None

    score_path = os.path.join(tmp_dir, "score.osc")
    # Generate OSC note-off at time 'dur' seconds (or earlier for short envs)
    note_off = max(dur, 0.05)

    prepare = f"""// Auto-generated prepare script
{modified}

Score([
    [0.0, [\\s_new, \\{synth_name}, 1000, 0, 1, \\freq, {freq}, \\amp, {amp}]],
    [{note_off}, [\\n_set, 1000, \\gate, 0]],
    [{note_off + 0.5}, [\\n_free, 1000]],
]).write("{score_path}".standardizePath);
0.exit;
"""
    prepare_path = os.path.join(tmp_dir, "prepare.scd")
    silent_path = os.path.join(tmp_dir, "silent.wav")
    output_path = os.path.join(tmp_dir, "output.wav")

    with open(prepare_path, "w") as f:
        f.write(prepare)

    make_silent_wav(silent_path, dur=max(dur + 1, 2.0))

    # Step 1: sclang — generate binary + score
    print(f"    sclang ...", end=" ", flush=True)
    t0 = time.time()
    try:
        res = subprocess.run(
            [SCLANG, prepare_path],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT (>20s)")
        print(f"      Possibly missing UGen or infinite loop in SynthDef")
        return "TIMEOUT"
    elapsed = time.time() - t0
    if res.returncode != 0:
        print(f"FAIL (exit={res.returncode})")
        for line in res.stderr.splitlines():
            if "ERROR" in line:
                print(f"      SC Error: {line.strip()}")
        return None
    # Check for SC errors in stdout/stderr
    sc_errors = []
    for line in (res.stdout + res.stderr).splitlines():
        if "ERROR" in line or "FAILURE" in line:
            sc_errors.append(line.strip())
    if sc_errors:
        for e in sc_errors:
            print(f"      SC Warning/Error: {e}")
    print(f"OK ({elapsed:.1f}s)")

    # Verify binary was written by .load
    scsyndef = os.path.join(SYNTHDEF_DIR, f"{synth_name}.scsyndef")
    if not os.path.exists(scsyndef):
        print(f"    ERROR: .scsyndef not found at {scsyndef}")
        return None

    # Step 2: scsynth — render WAV
    print(f"    scsynth ...", end=" ", flush=True)
    t0 = time.time()
    try:
        res = subprocess.run(
            [
                SCSYNTH,
                "-o", "2",
                "-N",
                score_path,
                silent_path,
                output_path,
                "44100",
                "WAV",
                "int16",
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT (>20s)")
        return "TIMEOUT"
    elapsed = time.time() - t0
    if res.returncode != 0:
        print(f"FAIL (exit={res.returncode})")
        for line in res.stderr.splitlines():
            if "ERROR" in line or "FAIL" in line:
                print(f"      {line.strip()}")
        return None
    sc_errors = []
    for line in (res.stdout + res.stderr).splitlines():
        if "ERROR" in line or "FAILURE" in line:
            sc_errors.append(line.strip())
    if sc_errors:
        for e in sc_errors:
            print(f"      SC Warning/Error: {e}")
    print(f"OK ({elapsed:.1f}s)")

    if not os.path.exists(output_path) or os.path.getsize(output_path) < 100:
        print(f"    ERROR: Output WAV too small or missing")
        return None

    return output_path


def test_synthdef(scd_path, synth_name, test_params):
    """Test a single SynthDef. Returns (name, pass, issues_list)."""
    with open(scd_path) as f:
        content = f.read()
    block = extract_synthdef_block(content, synth_name)
    if not block:
        print(f"  {synth_name}: Could not extract SynthDef block")
        return (synth_name, False, ["EXTRACTION_FAILED"])

    with tempfile.TemporaryDirectory(prefix="sc_test_") as tmp_dir:
        wav = nrt_render(block, tmp_dir, synth_name, test_params)
        if wav is None:
            return (synth_name, False, ["NRT_FAILED"])
        if wav == "TIMEOUT":
            return (synth_name, False, ["SCLANG_TIMEOUT"])
        ok, issues = analyze_wav(
            wav,
            expected_freq=test_params.get("freq"),
            label=f"{synth_name} @ {test_params.get('freq', '?')}Hz",
        )
        return (synth_name, ok, issues)


def main():
    parser = argparse.ArgumentParser(description="Test SuperCollider SynthDefs")
    parser.add_argument("files", nargs="+", help=".scd file(s) to test")
    parser.add_argument("--freq", type=float, nargs="+",
                        default=[262], help="Test frequencies (default: 262=C4)")
    parser.add_argument("--dur", type=float, default=1.0,
                        help="Note duration in seconds (default: 1.0)")
    parser.add_argument("--amp", type=float, default=0.5,
                        help="Amplitude (default: 0.5)")
    parser.add_argument("--synth", type=str, default=None,
                        help="Test only specific synth name")

    args = parser.parse_args()
    test_params = {
        "dur": args.dur,
        "amp": args.amp,
    }

    all_results = []

    for scd_path in args.files:
        if not os.path.exists(scd_path):
            print(f"File not found: {scd_path}")
            continue
        with open(scd_path) as f:
            content = f.read()
        names = find_synthdef_names(content)
        if not names:
            print(f"No SynthDefs found in {scd_path}")
            continue

        if args.synth:
            names = [n for n in names if n == args.synth]
            if not names:
                print(f"Synth '{args.synth}' not found in {scd_path}")
                continue

        print(f"\n=== {os.path.basename(scd_path)} ({len(names)} synths) ===")
        for name in names:
            for freq in args.freq:
                test_params["freq"] = freq
                _, ok, issues = test_synthdef(scd_path, name, test_params)
                status = "PASS" if ok else "FAIL"
                issue_str = "; ".join(issues) if isinstance(issues, list) else "-"
                print(f"  -> {status}: {issue_str}")
                all_results.append((scd_path, name, freq, ok, issues))

    print(f"\n{'='*60}")
    print(f"Summary:")
    passed = sum(1 for r in all_results if r[3])
    total = len(all_results)
    for r in all_results:
        path, name, freq, ok, issues = r
        status = "PASS" if ok else "FAIL"
        issue_str = "; ".join(issues[:2]) if issues else "-"
        print(f"  {status:4s}  {name:20s} @ {freq:7.1f}Hz  {issue_str}")
    print(f"\n{passed}/{total} passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
