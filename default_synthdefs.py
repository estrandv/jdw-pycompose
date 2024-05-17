def get() -> list[str]:
    synthdefs = []

    synthdefs.append("""
    SynthDef.new("pluck",
    {|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.01, decay=0.01, rel=0.01, peak=1, level=0.8|
    var osc, env;
    sus = sus * blur;
    freq = [freq, freq+fmod];
    amp=(amp + 1e-05);
    freq=(freq + [0, LFNoise2.ar(50).range(-2, 2)]);
    osc=((SinOsc.ar((freq * 1.002), phase: VarSaw.ar(freq, width: Line.ar(1, 0.2, 2))) * 0.3) + (SinOsc.ar(freq, phase: VarSaw.ar(freq, width: Line.ar(1, 0.2, 2))) * 0.3));
    osc=((osc * XLine.kr(amp, (amp / 10000), (sus * 4), doneAction: 2)) * 0.3);
    osc = Mix(osc) * 0.5;
    osc = Pan2.ar(osc, pan);
    Out.ar(bus, osc)})
    """)

    synthdefs.append("""
    SynthDef("pycompose",
    {|amp=1, sus=0.2, pan=0, bus=0, freq=440, cutoff=1000, rq=0.5, fmod=1, relT=0.04, fxa=1.0, fxf=300, fxs=0.002, fBus=0,gate=1|
        var osc1, osc2, filter, filter2, env, filterenv, ab;
        amp = amp * 0.2;
        freq = (freq + In.kr(fBus)) * fmod; 
        
        osc1 = Saw.ar(freq);
        osc2 = Mix(Saw.ar(freq * [0.125,1,1.5], [0.5,0.4,0.1]));
        osc2 = Mix(Saw.ar(freq * 2) * [fxs, 0.1], osc2);

        filterenv = EnvGen.ar(Env.adsr(0.0, 0.5, 0.2, sus), 1, doneAction:Done.none);
        filter =  RLPF.ar(osc1 + osc2, cutoff * filterenv + 100, rq);
        ab = abs(filter);
        filter2 = (filter * (ab + 2) / (filter ** 2 + 1 * ab + 1));
        filter2 = BLowShelf.ar(filter2, fxf, fxa, -12);
        filter2 = BPeakEQ.ar(filter2, 1600, 1.0, -6);

        env = EnvGen.ar(Env([0,1,0.8,0.8,0], [0.01, 0, sus, relT]), doneAction:Done.freeSelf);

        Out.ar(bus,Pan2.ar((filter + filter2) * env * amp, pan))
    })
    """)

    synthdefs.append("""
    SynthDef.new("brute",
    {|amp=1, sus=1, pan=0, freq=340, hpf=200, ace=0.6, fcx=4, prt=0, bus=0,
    attT=0.02, decT=0.0, susL=1.0, relT=0.0, gate=1, lfoS=0.0, lfoD=0.0, gain=1.0, fx=0.06|
    var osc, snd, env, gen, filterenv, filter, lfosc, snd2, saw1, saw2, saw3;

    amp = amp * gain;

    // Portamento
    freq = Lag.kr(freq, prt);

    /*
        Actual brute has some form of RLPF (resonance/cutoff)
        This filter is then applied with adsr
    */

    filterenv = Env.adsr(
    attackTime: fcx,
    sustainLevel: 0.2,
    releaseTime: fcx * 4,
    curve: -1.0,
    peakLevel: 2
    );

    // Example of above: [0.0--->0.2->0.5------>1.0---->0.0]
    // Current sound: When attack reaches max, we appear to drop to 0.0 amp for all freqs
    // As we transfer to sustain, we return to some kind of amp (this is because fcs is 0.5, so the filter amount lowers!)
    // WIth some more checks it would appear that the FILTER applies the same while AMP follows the adsr
    // As such it appears that MUL does not concern itself with any separate freqs, it's just output in total
    // I think the real solution is to have some form of crossfade
    // So that naked SND is favoured over filter when ADSR is low

    filterenv = EnvGen.kr(filterenv, gate, doneAction: Done.none);

    lfosc = SinOsc.kr(lfoS).range((1 - lfoD), 1);

    // Simple saw wave
    saw1 = Saw.ar(freq: lfosc * freq, mul: amp, add: 0.0);
    saw2 = Saw.ar(freq: lfosc * freq + (fx * 0.2), mul: amp, add: 0.0);
    saw3 = Saw.ar(freq: lfosc * freq + (fx * 1.5), mul: amp, add: 0.0);

    snd = saw1 + (saw2 * saw3);

    snd = RHPF.ar(
    in: snd,
    freq: hpf * filterenv,
    rq: ace * filterenv,
    mul: 1.0
    );

    // ADSR
    env = Env.adsr(
    attackTime: attT,
    decayTime: decT,
    sustainLevel: susL,
    releaseTime: relT,
    peakLevel: 1.0,
    curve: -4.0,
    bias: 0.0
    );

    gen = EnvGen.kr(env, gate, doneAction: Done.freeSelf);

    snd = snd * gen;

    // Mono to stereo
    snd = Mix(snd) * 0.5;

    // Panning
    snd = Pan2.ar(snd, pan);

    Out.ar(bus, snd)})
    """)

    synthdefs.append("""
    SynthDef.new("gentle",
    {|amp=1, gain=1, sus=1, pan=0, freq=440, prt=0, bus=0, hpf=20, lpf=8000, attT=0.02, decT=0.0, susL=1.0, relT=0.0, phase=0.5, gate=1, lfoS=0.02, lfoD=0.0|
    var osc, snd, env, gen;

    amp = amp * gain;

    freq = Lag.kr(freq, prt);

    osc = FSinOsc.ar(freq: freq, iphase: phase, mul: amp, add: 0.0);

    // ADSR
    env = Env.adsr(
        attackTime: attT,
        decayTime: decT,
        sustainLevel: susL,
        releaseTime: relT,
        peakLevel: 1.0,
        curve: -4.0,
        bias: 0.0
    );

    gen = EnvGen.kr(env, gate, doneAction: Done.freeSelf);

    osc = osc * (SinOsc.ar(lfoS * freq).range((1 - lfoD), 1));

    osc = osc * gen;

    // Mono to stereo
    snd = Mix(osc) * 0.5;

    // High/Low pass filter
    snd=HPF.ar(snd, hpf);
    snd=LPF.ar(snd, lpf);

    // Panning
    snd = Pan2.ar(snd, pan);

    Out.ar(bus, snd)})
    """)

    synthdefs.append("""

SynthDef.new("feedbackPad1", {
	arg
	// Standard Values
	out = 0, amp = 1, gate = 1, freq = 75, pan = 0,
	// Controls for ampEnv
	att = 2, dec = 1, sus = 1, rel = 4, crv = 0,
	// Controls for fbEnv
	fbStartStop = 0, fbAtt = 3, fbPeak = 0.8, fbDec = 2, fbSus = 0.67, fbRel = 5,
	// Confrols for delEnv
	delStartStop = 0.55, delAtt = 1, delPeak = 0, delDec = 2, delSus = 0.25, delRel = 3.5;

	var snd, fbIn, fbOut, ampEnv, fbEnv, delEnv;

	// Set up the Envelopes
	ampEnv = Env.adsr(
		attackTime: att,
		decayTime: dec,
		sustainLevel: sus,
		releaseTime: rel,
		curve: crv).ar(gate: gate);

	fbEnv = Env.adsr(
		attackTime: fbAtt,
		decayTime: fbDec,
		sustainLevel: fbSus,
		releaseTime: fbRel,
		peakLevel: fbPeak,
		curve: \lin,
		bias: fbStartStop).ar(gate: gate);

	delEnv = Env.adsr(
		attackTime: delAtt,
		decayTime: delDec,
		sustainLevel: delSus,
		releaseTime: delRel,
		peakLevel: delPeak,
		curve: \lin,
		bias: delStartStop).ar(gate: gate);

	// Receive the feedback
	fbIn = LocalIn.ar;

	// The Sound (yup, that's all it is)
	snd = SinOsc.ar(
		freq: freq,
		phase: fbIn * pi);

	// Delay the feedback
	fbOut = DelayC.ar(
		in: snd,
		maxdelaytime: delStartStop.max(delPeak.max(delSus)),
		delaytime: delEnv,
		mul: fbEnv);

	// Send the feedback
	LocalOut.ar(fbOut);

	// Output Stuff
	snd = Mix.ar(snd) * ampEnv * amp;
	snd = Limiter.ar(snd);

    DetectSilence.ar(in: snd, doneAction: 2);

	Out.ar(out, Pan2.ar(snd, pan))})
    
    
    """)


    # Effects 

    synthdefs.append("""
    SynthDef("reverb",
    {|amp=1, inBus=0, outBus=0, room=0.7, mix=0.33|
    var snd;
    snd = In.ar(inBus,1);
    snd = FreeVerb.ar(snd, mix: mix, room: room, damp: 0.5, mul: 1.0, add: 0.0);
    snd = Pan2.ar(snd, 0.0); // Always re-center! 
    Out.ar(outBus,snd)
    })
    """)

    # Bus control synth 
    synthdefs.append("""
    SynthDef("control",
    {|val=0,bus=0,prt=0|
    val = Lag.kr(val, prt);
    Out.kr(bus,val)
    })
    """)

    return synthdefs