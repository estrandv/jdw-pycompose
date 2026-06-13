#!/usr/bin/env python3
"""
Batch test SuperCollider SynthDefs and produce a summary table.

Usage:
    python3 batch_test.py                     # test all in new_synths/
    python3 batch_test.py path/to/synthDefs.scd   # test specific file
    python3 batch_test.py --freq 131 262 523  # test at multiple frequencies
"""

import argparse
import os
import sys
import subprocess
import shutil

SCD_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_SCRIPT = os.path.join(SCD_DIR, "test_synth.py")
DEFAULT_FREQS = [131, 262, 523]


def find_scd_files(paths):
    files = []
    for p in paths:
        if os.path.isfile(p):
            files.append(p)
        elif os.path.isdir(p):
            for f in sorted(os.listdir(p)):
                if f.endswith(".scd"):
                    files.append(os.path.join(p, f))
    return files


KNOWN_BROKEN = {
    "samplerALT": "needs buffer input",
    "router": "effect — needs audio input",
    "clamp": "effect — needs audio input",
    "delay": "effect — needs audio input",
    "controlMod": "control-only synth",
    "compressor": "effect — needs audio input",
    "tube": "stub (TODO)",
    "distortion": "effect — needs audio input",
    "analogTape": "effect — needs audio input",
    "analogChew": "missing UGen (sc3-plugins)",
    "reverb": "effect — needs audio input",
    "vverb": "effect — needs audio input",
}


def run_test(fpath, synth_name, freq, dur):
    """Run test_synth.py for a single synth/freq combo and parse result."""
    cmd = [
        sys.executable,
        TEST_SCRIPT,
        fpath,
        "--synth", synth_name,
        "--freq", str(freq),
        "--dur", str(dur),
    ]
    res = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = res.stdout + res.stderr

    # Parse result from output
    if "-> PASS:" in output:
        return "PASS"
    if "-> FAIL:" in output:
        # Extract issue
        for line in output.splitlines():
            if "-> FAIL:" in line:
                return "FAIL"
        return "FAIL"
    if "SCLANG_TIMEOUT" in output:
        return "TIMEOUT"
    if "NRT_FAILED" in output:
        return "NRT_ERR"
    return "???"


def main():
    parser = argparse.ArgumentParser(description="Batch test SuperCollider SynthDefs")
    parser.add_argument("paths", nargs="*", default=None,
                        help=".scd files or directories (default: scd/new_synths/)")
    parser.add_argument("--freq", type=float, nargs="+",
                        default=DEFAULT_FREQS, help="Test frequencies")
    parser.add_argument("--dur", type=float, default=1.0,
                        help="Note duration")
    parser.add_argument("--skip-broken", action="store_true", default=True,
                        help="Skip known-broken synths")
    args = parser.parse_args()

    if args.paths:
        files = find_scd_files(args.paths)
    else:
        new_synths = os.path.join(SCD_DIR, "new_synths")
        if os.path.isdir(new_synths):
            files = find_scd_files([new_synths])
        else:
            files = []

    if not files:
        files = [os.path.join(SCD_DIR, "synthDefs.scd")]
        if not os.path.exists(files[0]):
            print("No .scd files found")
            return 1

    # Collect all synth names from files
    import test_synth as ts
    all_results = []  # (synth_name, freq, status, issues)

    for fpath in files:
        with open(fpath) as f:
            content = f.read()
        names = ts.find_synthdef_names(content)
        if not names:
            continue

        print(f"\n--- {os.path.basename(fpath)} ({len(names)} synths) ---")
        for name in names:
            if args.skip_broken and name in KNOWN_BROKEN:
                reason = KNOWN_BROKEN[name]
                print(f"  {name:20s}  SKIP  ({reason})")
                for freq in args.freq:
                    all_results.append((name, freq, "SKIP", reason))
                continue

            print(f"  {name:20s}", end=" ", flush=True)
            freqs = []
            for freq in args.freq:
                status = run_test(fpath, name, freq, args.dur)
                freqs.append(status)
            status_str = ",".join(freqs)
            issues = []
            if "FAIL" in status_str:
                issues.append("FAIL at some freq")
            if "TIMEOUT" in status_str:
                issues.append("SCLANG timeout")
            print(f"  [{status_str}]  {'; '.join(issues)}")
            for i, freq in enumerate(args.freq):
                all_results.append((name, freq, freqs[i], issues))

    # Print summary table
    print(f"\n{'=' * 70}")
    print(f"{'Synth':20s} ", end="")
    for freq in args.freq:
        print(f"  {freq:5.0f}Hz ", end="")
    print(f"  Notes")
    print(f"{'-' * 20} ", end="")
    for _ in args.freq:
        print(f"  {'------'}", end="")
    print(f"  {'-----':s}")

    seen = set()
    for name, freq, status, issues in all_results:
        if name not in seen:
            seen.add(name)
            print(f"{name:20s} ", end="")
            row = [r for r in all_results if r[0] == name and r[1] in args.freq]
            status_map = {r[1]: r[2] for r in row}
            for freq in args.freq:
                s = status_map.get(freq, "?")
                print(f"  {s:6s}", end="")
            notes = ""
            if name in KNOWN_BROKEN:
                notes = f"({KNOWN_BROKEN[name]})"
            elif any(r[2] == "FAIL" for r in row):
                f_issues = [r[3] for r in row if r[3]]
                notes = "; ".join(
                    set(x for sub in f_issues for x in (sub if isinstance(sub, list) else [sub]))
                ) if f_issues else ""
            print(f"  {notes}")

    # Count
    total = len([r for r in all_results if r[0] not in KNOWN_BROKEN])
    passed = len([r for r in all_results if r[2] == "PASS"])
    failed = len([r for r in all_results if r[2] == "FAIL"])
    skipped = len([r for r in all_results if r[2] == "SKIP"])
    timeout = len([r for r in all_results if r[2] == "TIMEOUT"])
    print(f"\n{passed} passed, {failed} failed, {timeout} timeout, {skipped} skipped "
          f"({total} active tests)")

    return 0 if failed == 0 and timeout == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
