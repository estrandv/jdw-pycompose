// reeseBass — massive detuned saws with chorus
// Multiple detuned sawtooth waves with modulated comb filtering.
// The detune creates a thick, moving sound.
// NOTE: voice count is fixed at 5 because Mix.fill requires a compile-time constant.
SynthDef.new("reeseBass", {|amp=1, freq=440, gate=1, out=0, pan=0,
    att=0.01, decay=0.2, sus=0.8, rel=0.4,
    detune=0.04, cut=1500, rq=0.5,
    chorusRate=0.3, chorusDepth=0.004|
    var env, osc, chorus, filter, snd, rates;
    env = Env.adsr(att, decay, sus, rel).kr(gate: gate, doneAction: Done.freeSelf);
    osc = Mix.fill(5, {|i|
        var det = (i / 4 - 0.5) * 2 * detune;
        Saw.ar(freq * (1 + det)) / 5;
    });
    rates = [0.8, 1.0, 1.2];
    chorus = Mix.fill(3, {|i|
        DelayC.ar(osc, 0.03,
            LFNoise1.kr(chorusRate * rates[i]).range(0.001, chorusDepth * (i + 1))
        );
    });
    filter = RLPF.ar(osc + chorus * 0.5, cut, rq);
    snd = filter * env * amp;
    snd = LeakDC.ar(snd);
    snd = Pan2.ar(snd * 0.4, pan);
    Out.ar(out, snd);
})
