// syncLead — hard-synced oscillator lead
// One oscillator resets another at a harmonic ratio, creating
// the classic "sync sweep" sound. Mix with a pulse for body.
SynthDef.new("syncLead", {|amp=1, freq=440, gate=1, out=0, pan=0,
    att=0.01, decay=0.2, sus=0.7, rel=0.6,
    cut=3000, res=0.2, envMod=0.5,
    syncRatio=3, pw=0.5|
    var env, filterEnv, osc, snd;
    env = Env.adsr(att, decay, sus, rel, 1, -4)
        .kr(gate: gate, doneAction: Done.freeSelf);
    filterEnv = Env.adsr(att, decay, sus * 0.5, rel, 1, -4)
        .kr(gate: gate);
    osc = Mix([
        SyncSaw.ar(freq, freq * syncRatio, 0.6),
        Pulse.ar(freq, pw, 0.3),
    ]);
    snd = RLPF.ar(osc, cut * (1 + filterEnv * envMod), res);
    snd = snd * env * amp;
    snd = LeakDC.ar(snd);
    snd = Pan2.ar(snd * 0.5, pan);
    Out.ar(out, snd);
})
