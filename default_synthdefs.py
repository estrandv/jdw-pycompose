

# Standard: 
# - Top args should be exact same (and exist) for everyone, second row is occasional, third row is unique
# - "+++" divides
split_stack = """

SynthDef("eBass",
{|amp=1,freq=440,gate=1,out=0,pan=0,
    susT=0.2,relT=0.04,
    cutoff=200,rq=0.5,fmod=1,fxa=1.0,fxf=300,fxs=0.002,fBus=0|

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

    Out.ar(out,Pan2.ar((filter + filter2) * env * amp, pan))
})

+++

SynthDef(\FMRhodes, {|amp=1,freq=440,gate=1,out=0,pan=0,
    attT = 0.001, relT = 1, lfoS = 4.8, lfoD = 0.1
    inputLevel = 0.2, modIndex = 0.2, mix = 0.2|

    var env1, env2, env3, env4;
    var osc1, osc2, osc3, osc4, snd;

    env1 = Env.perc(attT, relT * 1.25, inputLevel, curve: \lin).kr;
    env2 = Env.perc(attT, relT, inputLevel, curve: \lin).kr;
    env3 = Env.perc(attT, relT * 1.5, inputLevel, curve: \lin).kr;
    env4 = Env.perc(attT, relT * 1.5, inputLevel, curve: \lin).kr;

    osc4 = SinOsc.ar(freq) * 6.7341546494171 * modIndex * env4;
    osc3 = SinOsc.ar(freq * 2, osc4) * env3;
    osc2 = SinOsc.ar(freq * 30) * 0.683729941 * env2;
    osc1 = SinOsc.ar(freq * 2, osc2) * env1;
    snd = Mix((osc3 * (1 - mix)) + (osc1 * mix));
  	snd = snd * (SinOsc.ar(lfoS).range((1 - lfoD), 1));

    snd = snd * Env.asr(0, 1, 0.1).kr(gate: gate, doneAction: Done.freeSelf);
    snd = Pan2.ar(snd, pan, amp);

    Out.ar(out, snd)})

+++

SynthDef("organReed", {|amp=1,freq=440,gate=1,out=0,pan=0,
    attT = 0.3, relT = 0.3,
    //Depth and Rate Controls (pwmDepth and amDepth range from 0 to 1)
    ranDepth = 0.04, pwmRate = 0.06, pwmDepth = 0.1, amDepth = 0.05, amRate = 5,
    //Other Controls
    nyquist = 18000, fHarmonic = 0.82, fFreq = 2442, rq = 0.3, hiFreq = 1200, hirs = 1, hidb = 1|

    var snd, env;

    // The same envelope controls both the resonant freq and the amplitude
    env = Env.asr(
        attackTime: attT,
        sustainLevel: amp,
        releaseTime: relT).ar(gate: gate, doneAction: Done.freeSelf);

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

    Out.ar(out, Pan2.ar(snd, pan))})
    
+++
SynthDef.new("pluck", {|amp=1,freq=440,gate=1,out=0,pan=0,
        susT=1, 
        fmod=0, blur=1|
    var osc, env;
    susT = susT * blur;
    freq = [freq, freq+fmod];
    amp=(amp + 1e-05) * 0.8;
    freq=(freq + [0, LFNoise2.ar(50).range(-2, 2)]);
    osc=((SinOsc.ar((freq * 1.002), phase: VarSaw.ar(freq, width: Line.ar(1, 0.2, 2))) * 0.3) + (SinOsc.ar(freq, phase: VarSaw.ar(freq, width: Line.ar(1, 0.2, 2))) * 0.3));
    osc=((osc * XLine.kr(amp, (amp / 10000), (susT * 4), doneAction: Done.freeSelf)) * 0.3);
    osc = Mix(osc) * 0.5;
    osc = Pan2.ar(osc, pan);
    Out.ar(out, osc)})

+++
SynthDef.new("blip",{|amp=1,freq=440,gate=1,out=0,pan=0,
    susT=1, fmod=0, rate=0, blur=1|
    var osc, env;
    susT = susT * blur;
    freq = [freq, freq+fmod];
    amp=(amp + 1e-05) * 0.8;
    freq=(freq + [0, LFNoise2.ar(50).range(-2, 2)]);
    freq=(freq * 2);
    osc=((LFCub.ar((freq * 1.002), iphase: 1.5) + (LFTri.ar(freq, iphase: Line.ar(2, 0, 0, 2)) * 0.3)) * Blip.ar((freq / 2), rate));
    osc=( (osc * XLine.ar(start: amp, end: (amp / 10000), dur: (susT * 2), doneAction: Done.freeSelf ) ) * 0.3 );
    osc = Mix(osc) * 0.5;
    osc = Pan2.ar(osc, pan);
	Out.ar(out, osc)})
+++
SynthDef.new("karp",{|amp=1,freq=440,gate=1,out=0,pan=0,
    susT=1, fmod=0, rate=22, blur=1|
    var osc, env;
    susT = susT * blur;
    freq = [freq, freq+fmod];
    amp=(amp * 0.4);
    osc=LFNoise0.ar((400 + (400 * rate)), amp);
    osc=(osc * XLine.ar(1, 1e-06, (susT * 0.1)));
    freq=((265 / (freq * 0.666)) * 0.005);
    osc=CombL.ar(osc, delaytime: freq, maxdelaytime: 2);
    env=EnvGen.ar(Env(times: [susT],levels: [(amp * 1), (amp * 1)],curve: 'step'), doneAction: Done.freeSelf);
    osc=(osc * env);
    osc = Mix(osc) * 0.5;
    osc = Pan2.ar(osc, pan);
	Out.ar(out, osc)})
+++
SynthDef.new("arpy",{|amp=1,freq=440,gate=1,out=0,pan=0,
    susT=1, fmod=0, blur=1|
    var osc, env;
    susT = susT * blur;
    freq = [freq, freq+fmod];
    freq=(freq / 2);
    amp=(amp * 2);
    freq=(freq + [0, 0.5]);
    osc=LPF.ar(Impulse.ar(freq), 3000);
    env=EnvGen.ar(Env.perc(attackTime: 0.01, releaseTime: susT * 0.25, level: amp, curve: 0), doneAction: Done.freeSelf);
    osc=(osc * env);
    osc = Mix(osc) * 0.5;
    osc = Pan2.ar(osc, pan);
	Out.ar(out, osc)})
+++
SynthDef("prophet",{|amp=1,freq=440,gate=1,out=0,pan=0,
    susT=0.1,
	lfoS=1, lfoD=0.5, cutoff=6000, rq=0.4|

    var lfo, pulse, filter, env;
    amp = amp * 0.1;

    lfo = LFTri.kr(lfoS * [1, 1.01], Rand(0, 2.0)!2);

    pulse = Pulse.ar(freq * [1, 1.01], lfo * lfoD + 0.5);

    filter = RLPF.ar(pulse, cutoff, rq);

    filter = BHiPass.ar(filter, 200);

    env = EnvGen.ar(Env([0,1,0.8,0.8,0], [0.01, 0, susT, susT]), doneAction:Done.freeSelf);

    Out.ar(out, Pan2.ar(Mix(filter) * env * amp * 0.5, pan))})
+++

SynthDef("ksBass", {|amp=1,freq=440,gate=1,out=0,pan=0,
	relT = 1.5,
    // Parameters for the impulse shape
	attT = 0.5, susT = 1, impulseDec = 0.5, impulseHold = 1,
	// Filter and compressor parameters, thresh goes from 0 to 1.
	filtermin = 250, filtermax = 5000, rq = 0.35, thresh = 0.4, ratio = 2.5|

	var total, exciter, snd;

	// Rescale impulse values for the frequency of the note
	total = (attT + susT + impulseDec + impulseHold) * freq;

	// Initial impulse
	exciter = Env.new(
		levels: [0, 1, 1, 0, 0],
		times: [attT, susT, impulseDec, impulseHold]/total).ar;

	// Delay line
	snd = CombN.ar(
		in: exciter,
		maxdelaytime: 0.06,
		delaytime: 1/freq,
		decaytime: relT);

	// LPF
	snd = RLPF.ar(
		in: snd,
		freq: LinExp.ar(Amplitude.ar(in: snd), 0, 1, filtermin, filtermax),
		rq: rq);
	
	// Compressor for fun
	snd = CompanderD.ar(
		in: snd, 
		thresh: thresh, 
		slopeBelow: 1, 
		slopeAbove: 1/ratio);

	// Output stuff
	snd = Mix.ar(snd) * amp;
	snd = Limiter.ar(snd);

	DetectSilence.ar(in: snd, doneAction: Done.freeSelf);

    Out.ar(out, Pan2.ar(snd, pan))})


+++

SynthDef.new("dBass", {|amp=1,freq=440,gate=1,out=0,pan=0,
	susT=1, fmod=0, rate=0|
		var osc, env;
		freq = [freq, freq+fmod] * Line.ar(Rand(0.5,1.5),1,0.02);
		amp=(amp * 0.1);
		osc=( VarSaw.ar(freq, width: LFTri.ar((0.5 * rate)/susT, iphase:0.9, add:0.8, mul: 0.2), mul: amp));
		env=EnvGen.ar(Env([0,1,0.8,0.8,0], [0.02, 0.01, susT/2, susT/2]), doneAction: Done.freeSelf);
		osc=(osc * env);
		osc = Mix(osc) * 0.5;
		osc = Pan2.ar(osc, pan);
		Out.ar(out, osc)})

+++

SynthDef("feedbackPad", {|amp=1,freq=440,gate=1,out=0,pan=0,
	// Envelope Controls
	attT = 3, decT = 1, susL = 1, relT = 5, 
    crv = 0,
	// Other Controls (interval is in semitones)
	sampleRate = 2, notes = 3, interval = 14|

	var env, fbIn, snd;

	// Set up the Envelopes
	env = Env.adsr(
		attackTime: attT,
		decayTime: decT,
		sustainLevel: susL,
		releaseTime: relT,
		curve: crv).ar(gate: gate);

	// Receive and Sample the feedback
	fbIn = Latch.ar(
		in: (LocalIn.ar + 1)/2,
		trig: Impulse.ar(
			freq: sampleRate));
	fbIn = (fbIn * notes.abs * env).round(1);
	fbIn = (fbIn * interval).midiratio;

	// Make The Sound
	snd = LFTri.ar(
		freq: freq * fbIn,
		mul: env);

	// Feedback the Sound
	LocalOut.ar(snd);

	//Filter the Sound
	snd = RHPF.ar(
		in: snd,
		freq: freq,
		rq: 0.5);
	snd = LPF.ar(
		in: snd,
		freq: [62, 125, 250, 500, 1000, 2000, 4000, 8000, 16000],
		mul: 1/9);

	// Output Stuff
	snd = Mix.ar(snd) * amp;
	snd = Limiter.ar(snd);

	DetectSilence.ar(in: snd, doneAction: Done.freeSelf);

	Out.ar(out, Pan2.ar(snd, pan))})

+++


SynthDef("aPad", {|amp=1,freq=440,gate=1,out=0,pan=0,
	//Standard Values:
	attT = 0.4, decT = 0.5, susL = 0.8, relT = 1.0,
	//Other Controls:
	vibratoRate = 4, vibratoDepth = 0.015, tremoloRate = 5,
	//These controls go from 0 to 1:
	tremoloDepth = 0.5|

	var env, snd, vibrato, tremolo, mod2, mod3;

    amp = amp * 0.1;

	env = Env.adsr(attT, decT, susL, relT).kr(gate: gate);
	vibrato = SinOsc.kr(vibratoRate).range(freq * (1 - vibratoDepth), freq * (1 + vibratoDepth));
	tremolo = LFNoise2.kr(1).range(0.2, 1) * SinOsc.kr(tremoloRate).range((1 - tremoloDepth), 1);

	snd = SinOsc.ar(freq: [freq, vibrato], mul:(env * tremolo * amp)).distort;
	snd = Mix.ar([snd]);

	DetectSilence.ar(snd, 0.0001, 0.2, doneAction: Done.freeSelf);
	Out.ar(out, Pan2.ar(snd, pan))})


+++

SynthDef("moogBass", {|amp=1,freq=440,gate=1,out=0,pan=0,
    attT=0.001,decL=0.3,susT=0.9,relT=0.2
	cutoff=1000, gain=2.0, prt=0.01, chorus=0.7|

	var osc, filter, env, filterenv, snd, chorusfx;

	osc = Mix(VarSaw.ar(
		freq: freq.lag(prt) * [1.0, 1.001, 2.0],
		iphase: Rand(0.0,1.0) ! 3,
		width: Rand(0.5,0.75) ! 3,
		mul: 0.5));

	filterenv = EnvGen.ar(
		envelope: Env.asr(0.2, 1, 0.2),
		gate: gate);

	filter =  MoogFF.ar(
		in: osc,
		freq: cutoff * (1.0 + (0.5 * filterenv)),
		gain: gain);

	env = EnvGen.ar(
		envelope: Env.adsr(attT, decL, susT, relT, amp),
		gate: gate,
		doneAction: Done.freeSelf);

	snd = (0.7 * filter + (0.3 * filter.distort)) * env;

	chorusfx = Mix.fill(7, {

		var maxdelaytime = rrand(0.005, 0.02);
		DelayC.ar(
			in: snd,
			maxdelaytime: maxdelaytime,
			delaytime: LFNoise1.kr(
				freq: Rand(4.5, 10.5),
				mul: 0.25 * maxdelaytime,
				add: 0.75 * maxdelaytime)
		)
	});

	snd = snd + (chorusfx * chorus);

	Out.ar(out, Pan2.ar(snd, pan))})

+++

SynthDef("samplerALT", { |out = 0, start = 0, susT = 15, amp = 1, rate = 1, buf = 0, pan = 0, ofs=0.0,
        relT=0.05, lfoS=440, lfoD=0.0|
    var osc, env;

    // TODO: LFO on rate that isn't terror

    osc = PlayBuf.ar(1, buf, BufRateScale.kr(buf) * rate, startPos: start);
    amp = amp * 2.0; // I have found that sample amp usually lands way lower than any synth amp
    osc = osc * EnvGen.ar(Env([0,1 * amp,1 * amp,0],[ofs, susT-0.05, relT]), doneAction: Done.freeSelf);
    osc = Mix(osc);
    osc = Pan2.ar(osc, pan);

	Out.ar(out, osc)})

+++

// Effects below

SynthDef("router",
    {|in=0,out=0|
    Out.ar(out,In.ar(in,2))})

+++


SynthDef("clamp",
    {|bus=0, over=0, under=9000, mul=1.0, add=0.0|
    var snd;
    snd = In.ar(bus,2);
    snd = HPF.ar(in: snd, freq: over, mul: mul, add: add);
    snd = LPF.ar(in: snd, freq: under, mul: mul, add: add);
    ReplaceOut.ar(bus,snd)})

+++

SynthDef.new("delay", {|bus=0, echo=0.25, beat_dur=1, echt=1.0|
var osc;
osc = In.ar(bus, 2);
osc = osc + CombL.ar(osc, delaytime: echo * beat_dur, maxdelaytime: 2 * beat_dur, decaytime: echt * beat_dur);
ReplaceOut.ar(bus, osc)})

+++

SynthDef.new("distortion", {|bus=0, drive=0.5|
    var osc;
    osc = In.ar(bus, 2);
    osc = (osc * (drive * 50)).clip(0,0.2).fold2(2);
    Out.ar(bus, osc)})

+++

SynthDef("reverb",
    {|amp=1, bus=0, room=0.7, mix=0.33, damp=0.5,mul=1.0,add=0.0|
    var snd;
    snd = In.ar(bus,2);
    snd = FreeVerb.ar(snd, mix: mix, room: room, damp: damp, mul: mul, add: add);
    Out.ar(bus,snd)})




"""



def get() -> list[str]:
    synthdefs = split_stack.split("+++")
    return synthdefs