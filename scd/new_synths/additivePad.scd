// additivePad — sine harmonic pad
// 8 harmonics with individual level controls and progressive detune.
SynthDef.new("additivePad", {|amp=1, freq=440, gate=1, out=0, pan=0,
    att=1.0, decay=0.5, sus=1, rel=2.0,
    h1=1, h2=0.7, h3=0.5, h4=0.3, h5=0.2, h6=0.1, h7=0.05, h8=0.03,
    detune=0.003, spread=0.5|
    var env, snd;
    env = Env.adsr(att, decay, sus, rel, 1, -4)
        .kr(gate: gate, doneAction: Done.freeSelf);

    snd = Mix.fill(8, {|i|
        var partial = i + 1;
        var level = [h1, h2, h3, h4, h5, h6, h7, h8][i];
        var det = (i / 7 - 0.5) * 2 * detune;
        SinOsc.ar(freq * partial * (1 + det), mul: level * amp / 8);
    });

    snd = snd * env;
    snd = LeakDC.ar(snd);
    snd = Splay.ar(snd, spread);
    Out.ar(out, snd);
})
