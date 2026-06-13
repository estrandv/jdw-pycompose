// pluckBass — electric bass-style plucked string
// Triangle wave harmonics with fast-decaying envelope and body resonance.
// Warmer and more "wooden" than saw-based basses.
// NOTE: Env curve param must be a literal (not a synth control param).
SynthDef.new("pluckBass", {|amp=1, freq=440, gate=1, out=0, pan=0,
    att=0.005, decay=0.4, rel=0.3,
    cut=1500, rq=0.5, harmMix=0.3, bodyDecay=0.3|
    var env, snd, body;
    env = Env([0, 1, 0.4, 0], [att, decay, rel], [-4, -4, -4])
        .kr(gate: gate, doneAction: Done.freeSelf);
    snd = Mix([
        LFTri.ar(freq, mul: 0.3),
        LFTri.ar(freq * 2.01, mul: 0.12),
        LFTri.ar(freq * 3.02, mul: 0.05),
        LFTri.ar(freq * 4.03, mul: 0.03),
    ]);
    body = Ringz.ar(snd, freq * 2, bodyDecay) * 0.15;
    snd = RLPF.ar(snd + body, cut * (1 + env * 1.5), rq);
    snd = snd * env * amp;
    snd = LeakDC.ar(snd);
    snd = Limiter.ar(snd, 0.9);
    snd = Pan2.ar(snd * 0.5, pan);
    Out.ar(out, snd);
})
