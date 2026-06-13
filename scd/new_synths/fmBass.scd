// fmBass — 2-operator FM bass with pitch envelope
// Classic DX-style bass: carrier modulated by a harmonic, modulation index decays
// giving the characteristic "punchy" transient.
SynthDef.new("fmBass", {|amp=1, freq=440, gate=1, out=0, pan=0,
    att=0.01, decay=0.3, sus=0.6, rel=0.15,
    ratio=0.5, idxAtt=0.005, idxDecay=0.25, idxSus=0.05, idxRel=0.05, idxPeak=4,
    cut=3000, rq=0.4|
    var env, idxEnv, mod, car, snd;
    env = Env.adsr(att, decay, sus, rel).kr(gate: gate, doneAction: Done.freeSelf);
    idxEnv = Env.adsr(idxAtt, idxDecay, idxSus, idxRel, idxPeak, -4).kr(gate: gate);
    mod = SinOsc.ar(freq * ratio, mul: idxEnv * freq * ratio);
    car = SinOsc.ar(freq + mod);
    snd = car * env * amp;
    snd = RLPF.ar(snd, cut, rq);
    snd = LeakDC.ar(snd);
    snd = Mix(snd) * 0.5;
    snd = Pan2.ar(snd, pan);
    Out.ar(out, snd);
})
