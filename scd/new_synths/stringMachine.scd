// stringMachine — Solina-style ensemble of detuned saws
// 4 detuned saw waves through a chorus effect and LP filter.
SynthDef.new("stringMachine", {|amp=1, freq=440, gate=1, out=0, pan=0,
    att=0.1, decay=0.3, sus=0.8, rel=1.0,
    detune=0.007, cut=4000, rq=0.7, chorusRate=0.4, chorusDepth=0.005|
    var env, osc, chorus, snd;
    env = Env.adsr(att, decay, sus, rel, 1, -4)
        .kr(gate: gate, doneAction: Done.freeSelf);

    osc = Mix([
        Saw.ar(freq * (1 - detune), 0.3),
        Saw.ar(freq, 0.3),
        Saw.ar(freq * (1 + detune), 0.3),
        Saw.ar(freq * 2 + 0.5, 0.15),
    ]);

    chorus = Mix.fill(2, {|i|
        var rate = [0.8, 1.2][i] * chorusRate;
        var mod = LFNoise1.kr(rate).exprange(0.002, chorusDepth * (i + 1) + 0.002);
        DelayC.ar(osc, 0.05, mod);
    });

    snd = RLPF.ar(osc + chorus * 0.5, cut, rq);
    snd = snd * env * amp;
    snd = LeakDC.ar(snd);
    snd = Pan2.ar(snd * 0.35, pan);
    Out.ar(out, snd);
})
