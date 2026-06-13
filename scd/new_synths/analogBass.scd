// analogBass — Minimoog-style multi-oscillator subtractive bass
// Three oscillators (two detuned saws + one pulse) through Moog ladder filter.
// Classic rich analogue bass tone.
SynthDef.new("analogBass", {|amp=1, freq=440, gate=1, out=0, pan=0,
    att=0.01, decay=0.3, sus=0.35, rel=0.4,
    cut=800, res=0.4, envMod=0.6, drive=0.15,
    pw=0.5, detune=0.005|
    var env, filterEnv, osc, filter, snd;
    env = Env.adsr(att, decay, sus, rel, 1, -4)
        .kr(gate: gate, doneAction: Done.freeSelf);
    filterEnv = Env.adsr(att, decay, sus, rel * 1.5, 1, -4)
        .kr(gate: gate);
    osc = Mix([
        Saw.ar(freq * (1 - detune), 0.35),
        Saw.ar(freq * (1 + detune), 0.35),
        Pulse.ar(freq, pw, 0.3),
    ]);
    filter = MoogFF.ar(
        osc,
        freq: cut * (1 + filterEnv * envMod),
        gain: res
    );
    snd = filter * env * amp;
    snd = (snd * (1 - drive)) + ((snd * 2).distort * drive * 0.5);
    snd = LeakDC.ar(snd);
    snd = Pan2.ar(snd * 0.5, pan);
    Out.ar(out, snd);
})
