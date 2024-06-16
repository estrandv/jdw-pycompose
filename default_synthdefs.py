def get() -> list[str]:
    synthdefs = []

    synthdefs.append("""
    SynthDef.new("pluck",
    {|amp=1, susT=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.01, decay=0.01, rel=0.01, peak=1, level=0.8|
    var osc, env;
    susT = susT * blur;
    freq = [freq, freq+fmod];
    amp=(amp + 1e-05);
    freq=(freq + [0, LFNoise2.ar(50).range(-2, 2)]);
    osc=((SinOsc.ar((freq * 1.002), phase: VarSaw.ar(freq, width: Line.ar(1, 0.2, 2))) * 0.3) + (SinOsc.ar(freq, phase: VarSaw.ar(freq, width: Line.ar(1, 0.2, 2))) * 0.3));
    osc=((osc * XLine.kr(amp, (amp / 10000), (susT * 4), doneAction: 2)) * 0.3);
    osc = Mix(osc) * 0.5;
    osc = Pan2.ar(osc, pan);
    Out.ar(bus, osc)})
    """)

    synthdefs.append("""
    SynthDef("pycompose",
    {|amp=1, susT=0.2, pan=0, bus=0, freq=440, cutoff=1000, rq=0.5, fmod=1, relT=0.04, fxa=1.0, fxf=300, fxs=0.002, fBus=0,gate=1|
        var osc1, osc2, filter, filter2, env, filterenv, ab;
        amp = amp * 0.2;
        freq = (freq * (In.kr(fBus) + 1)) * fmod; 
        
        osc1 = Saw.ar(freq);
        osc2 = Mix(Saw.ar(freq * [0.125,1,1.5], [0.5,0.4,0.1]));
        osc2 = Mix(Saw.ar(freq * 2) * [fxs, 0.1], osc2);

        filterenv = EnvGen.ar(Env.adsr(0.0, 0.5, 0.2, susT), 1, doneAction:Done.none);
        filter =  RLPF.ar(osc1 + osc2, cutoff * filterenv + 100, rq);
        ab = abs(filter);
        filter2 = (filter * (ab + 2) / (filter ** 2 + 1 * ab + 1));
        filter2 = BLowShelf.ar(filter2, fxf, fxa, -12);
        filter2 = BPeakEQ.ar(filter2, 1600, 1.0, -6);

        env = EnvGen.ar(Env([0,1,0.8,0.8,0], [0.01, 0, susT, relT]), gate: gate,doneAction:Done.freeSelf);

        Out.ar(bus,Pan2.ar((filter + filter2) * env * amp, pan))
    })
    """)

    synthdefs.append("""
    
SynthDef(\FMRhodes, {|out = 0, freq = 440, gate = 1, pan = 0, amp = 0.1, attT = 0.001, rel = 1, lfoS = 4.8, inputLevel = 0.2,
    // all of these range from 0 to 1
    modIndex = 0.2, mix = 0.2, lfoD = 0.1|

    var env1, env2, env3, env4;
    var osc1, osc2, osc3, osc4, snd;

    env1 = Env.perc(attT, rel * 1.25, inputLevel, curve: \lin).kr;
    env2 = Env.perc(attT, rel, inputLevel, curve: \lin).kr;
    env3 = Env.perc(attT, rel * 1.5, inputLevel, curve: \lin).kr;
    env4 = Env.perc(attT, rel * 1.5, inputLevel, curve: \lin).kr;

    osc4 = SinOsc.ar(freq) * 6.7341546494171 * modIndex * env4;
    osc3 = SinOsc.ar(freq * 2, osc4) * env3;
    osc2 = SinOsc.ar(freq * 30) * 0.683729941 * env2;
    osc1 = SinOsc.ar(freq * 2, osc2) * env1;
    snd = Mix((osc3 * (1 - mix)) + (osc1 * mix));
  	snd = snd * (SinOsc.ar(lfoS).range((1 - lfoD), 1));

    snd = snd * Env.asr(0, 1, 0.1).kr(gate: gate, doneAction: 2);
    snd = Pan2.ar(snd, pan, amp);

    Out.ar(out, snd)})
    
    """)

    synthdefs.append("""
    SynthDef.new("brute",
    {|amp=1, sus=1, pan=0, freq=340, hpf=200, ace=0.6, fcx=4, prt=0, bus=0,
    attT=0.02, decT=0.0, susL=1.0, relT=0.0, gate=1, lfoS=0.0, lfoD=0.0, lfBS=0, lfBD=0, gain=1.0, fx=0.06|
    var osc, snd, env, gen, filterenv, filter, lfosc, snd2, saw1, saw2, saw3;

    amp = amp * gain;

    lfoS = lfoS * In.kr(lfBS);
    lfoD = lfoD * In.kr(lfBD);

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

SynthDef.new("feedbackPad", {
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

    synthdefs.append("""
    
    // Overrides default in jdw-sc - used for shared-arg-bug hunting
SynthDef("sampler", { |bus = 0, start = 0, sus = 10, amp = 1, rate = 1, buf = 0, pan = 0, ofs=0.05|
    var osc = PlayBuf.ar(1, buf, BufRateScale.kr(buf) * rate, startPos: start);
    amp = amp * 2.0; // I have found that sample amp usually lands way lower than any synth amp
    osc = osc * EnvGen.ar(Env([0,1 * amp,1 * amp,0],[ofs, sus-0.05, 0.05]), doneAction: Done.freeSelf);
    osc = Mix(osc);
    osc = Pan2.ar(osc, pan);
	Out.ar(bus, osc)
})
    
    
    """)

    synthdefs.append("""
    
    SynthDef(\strings, {
	arg
	//Standard Definitions
	out = 0, freq = 440, amp = 1, gate = 1, pan = 0, freqLag = 0.2, att = 0.001, dec = 0.1, sus = 0.75, rel = 0.3,
	//Other Controls (mix ranges from 0 - 1)
	rq = 0.001, combHarmonic = 4, sawHarmonic = 1.5, mix = 0.33;

	var env, snd, combFreq;

	combFreq = 1 / (Lag.kr(in: freq, lagTime: freqLag / 2) * combHarmonic);

	env = Env.adsr(att, dec, sus, rel, amp).kr(gate: gate, doneAction: 2);

	snd = SyncSaw.ar(syncFreq: freq * WhiteNoise.kr().range(1/1.025, 1.025), sawFreq: freq * sawHarmonic, mul: 8);
	snd = (snd * (1 - mix)) + PinkNoise.ar(180 * mix);
	snd = CombL.ar(snd, combFreq, combFreq, -1); //Try positive 1 for decay time as well.
	snd = Resonz.ar(snd, Lag.kr(in: freq, lagTime: freqLag), rq).abs;
	snd = snd * env;
	snd = Limiter.ar(snd, amp);

	Out.ar(out, Pan2.ar(snd, pan))
})
    
    
    """)

    synthdefs.append("""
    
    
    SynthDef("organReed", {
    arg
	//Standard Values
	out = 0, pan = 0, freq = 440, amp = 0.3, gate = 1, att = 0.3, rel = 0.3,
	//Depth and Rate Controls (pwmDepth and amDepth range from 0 to 1)
	ranDepth = 0.04, pwmRate = 0.06, pwmDepth = 0.1, amDepth = 0.05, amRate = 5,
	//Other Controls
	nyquist = 18000, fHarmonic = 0.82, fFreq = 2442, rq = 0.3, hiFreq = 1200, hirs = 1, hidb = 1;

    var snd, env;

	// The same envelope controls both the resonant freq and the amplitude
    env = Env.asr(
		attackTime: att,
		sustainLevel: amp,
		releaseTime: rel).ar(gate: gate, doneAction: 2);

    // pulse with modulating width
	snd = Pulse.ar(
		freq: TRand.ar(lo: 2.pow(-1 * ranDepth), hi: 2.pow(ranDepth), trig: gate) * freq,
		width: LFNoise1.kr(freq: pwmRate, mul: pwmDepth).range(0, 1),
		mul: 0.0625);  //Incereasing this lessens the impact of the BPF

    // add a little "grit" to the reed
    //original used snd = Disintegrator.ar(snd, 0.5, 0.7);
	snd = Latch.ar(snd, Impulse.ar(nyquist * 2));

    // a little ebb and flow in volume
	snd = snd * LFNoise2.kr(freq: amRate).range((1 - amDepth), 1);

	//Filtering (BHiShelf intensifies the buzzing)
	snd = snd + BPF.ar(in: snd, freq: env.linexp(0, amp, fFreq * fHarmonic, fFreq), rq: rq);
    snd = BHiShelf.ar(in: snd, freq: hiFreq, rs: hirs, db: hidb);

	//Output
	snd = Mix.ar(snd * env);

    Out.ar(out, Pan2.ar(snd, pan))

})
    
    
    
    
    
    
    """)


    # Effects 

    synthdefs.append("""
    SynthDef("reverb",
    {|amp=1, inBus=0, outBus=0, room=0.7, mix=0.33, damp=0.5,mul=1.0,add=0.0|
    var snd;
    snd = In.ar(inBus,1);
    snd = FreeVerb.ar(snd, mix: mix, room: room, damp: damp, mul: mul, add: add);
    snd = Pan2.ar(snd, 0.0); // Always re-center! 
    Out.ar(outBus,snd)
    })
    """)

    # 

    synthdefs.append("""
    SynthDef("lowpass",
    {|in=0, out=0, freq=8000, mul=1.0, add=0.0|
    var snd;
    snd = In.ar(in,1);
    snd = LPF.ar(in: snd, freq: freq, mul: mul, add: add);
    snd = Pan2.ar(snd, 0.0); // Always re-center! 
    Out.ar(out,snd)
    })
    """)


    synthdefs.append("""
    SynthDef("highpass",
    {|in=0, out=0, freq=8000, mul=1.0, add=0.0|
    var snd;
    snd = In.ar(in,1);
    snd = HPF.ar(in: snd, freq: freq, mul: mul, add: add);
    snd = Pan2.ar(snd, 0.0); // Always re-center! 
    Out.ar(out,snd)
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