// subBass — clean sub-bass with sine + square blend
// Minimal and clean, for deep house / techno sub-bass.
// Sine provides the pure fundamental, square adds upper harmonics for presence.
SynthDef.new("subBass", {|amp=1, freq=440, gate=1, out=0, pan=0,
    att=0.005, decay=0.1, sus=1, rel=0.05,
    sineMix=0.6|
    var env, sine, square, snd;
    env = Env.adsr(att, decay, sus, rel).kr(gate: gate, doneAction: Done.freeSelf);
    sine = SinOsc.ar(freq);
    square = Pulse.ar(freq, 0.5) * 0.3;
    snd = (sine * sineMix + square * (1 - sineMix)) * env * amp;
    snd = LeakDC.ar(snd);
    snd = Pan2.ar(snd * 0.5, pan);
    Out.ar(out, snd);
})
