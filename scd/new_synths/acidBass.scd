// acidBass — 303-style resonant squelch
// Saw/square through resonant low-pass filter with envelope follower.
// The filter envelope is the main source of character.
SynthDef.new("acidBass", {|amp=1, freq=440, gate=1, out=0, pan=0,
    att=0.002, decay=0.8, sus=0.5, rel=0.05,
    cut=200, res=0.6, envMod=4, accent=0,
    waveform=0|
    var env, filterEnv, osc, filter, snd;
    env = Env.adsr(att, decay, sus, rel).kr(gate: gate, doneAction: Done.freeSelf);
    filterEnv = Env.perc(att, decay * 0.9, 1, -4).kr(gate: gate);
    osc = Select.ar(waveform, [
        Saw.ar(freq),
        Pulse.ar(freq, 0.5)
    ]);
    filter = MoogFF.ar(osc,
        freq: cut + (filterEnv * envMod * 500) + (accent * 1500),
        gain: res
    );
    snd = filter * env * amp;
    snd = LeakDC.ar(snd);
    snd = Pan2.ar(snd * 0.5, pan);
    Out.ar(out, snd);
})
