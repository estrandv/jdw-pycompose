// pwmPad — pulse wave with LFO-modulated width
// 3 detuned pulse waves with synchronized PWM via LFO.
SynthDef.new("pwmPad", {|amp=1, freq=440, gate=1, out=0, pan=0,
    att=0.5, decay=0.3, sus=0.8, rel=1.5,
    cut=4000, rq=0.5, detune=0.005,
    lfoRate=0.3, lfoDepth=0.4|
    var env, lfo, osc, snd;
    env = Env.adsr(att, decay, sus, rel, 1, -4)
        .kr(gate: gate, doneAction: Done.freeSelf);

    lfo = LFTri.kr(lfoRate).range(0.1, 0.9);

    osc = Mix.fill(3, {|i|
        var det = (i / 2 - 0.5) * 2 * detune;
        var pw = lfo * lfoDepth + (1 - lfoDepth) * 0.5;
        Pulse.ar(freq * (1 + det), pw, 1/3);
    });

    snd = RLPF.ar(osc, cut, rq);
    snd = snd * env * amp;
    snd = LeakDC.ar(snd);
    snd = Pan2.ar(snd * 0.5, pan);
    Out.ar(out, snd);
})
