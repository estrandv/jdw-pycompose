SynthDef.new("experimental",
{|amp=1,freq=440,gate=1,out=0,pan=0,
    susT=1, fmod=0, rate=0, attT=0, decT=0, susL=1,relT=0.5,fxi=0.5,fxii=0.1,prt=0.2|
    var osc, env, lfo, saw1, saw2;

    freq = freq.lag(prt);
    freq = [freq, freq+fmod];
    freq=(freq * [1, 1.005]);
    lfo = SinOsc.ar(1.222, mul: 1.0);
    saw1 = VarSaw.ar(freq, mul: (amp / 4) * lfo, width: 1);
    saw2 = Saw.ar(freq * 2.0002, mul: amp * fxii, width: fxi);
    osc= saw1 + saw2;
	env = Env.adsr(attT, decT, susL, relT);
    env = EnvGen.ar(envelope: env, gate: gate, doneAction: Done.freeSelf);
    osc = (osc * env);
    osc = Mix(osc) * 0.5;
    osc = Pan2.ar(osc, pan);
    Out.ar(out, osc)})


SynthDef.new("eBass",
{|amp=1,freq=440,gate=1,out=0,pan=0,
    susT=0.2,relT=0.04,
    cut=200,rq=0.5,fmod=1,fxa=1.0,fxf=300,fxs=0.002,fBus=0|

    var osc1, osc2, filter, filter2, env, filterenv, ab;
    amp = amp * 0.2;
    freq = (freq * (In.kr(fBus) + 1)) * fmod;

    osc1 = Saw.ar(freq);
    osc2 = Mix(Saw.ar(freq * [0.125,1,1.5], [0.5,0.4,0.1]));
    osc2 = Mix(Saw.ar(freq * 2) * [fxs, 0.1], osc2);

    filterenv = EnvGen.ar(Env.adsr(0.0, 0.5, 0.2, susT), 1, doneAction:Done.none);
    filter =  RLPF.ar(osc1 + osc2, cut * filterenv + 100, rq);
    ab = abs(filter);
    filter2 = (filter * (ab + 2) / (filter ** 2 + 1 * ab + 1));
    filter2 = BLowShelf.ar(filter2, fxf, fxa, -12);
    filter2 = BPeakEQ.ar(filter2, 1600, 1.0, -6);

    env = EnvGen.ar(Env([0,1,0.8,0.8,0], [0.01, 0, susT, relT]), gate: gate,doneAction:Done.freeSelf);

    Out.ar(out,Pan2.ar((filter + filter2) * env * amp, pan))
})



SynthDef.new("FMRhodes", {|amp=1,freq=440,gate=1,out=0,pan=0,
    attT = 0.001, relT = 1, fxi = 4.8, fxii = 0.1
    amod = 0.2, fxiii = 0.2, fxiv = 0.2|

    var env1, env2, env3, env4;
    var osc1, osc2, osc3, osc4, snd;

    env1 = Env.perc(attT, relT * 1.25, amod, curve: \lin).kr;
    env2 = Env.perc(attT, relT, amod, curve: \lin).kr;
    env3 = Env.perc(attT, relT * 1.5, amod, curve: \lin).kr;
    env4 = Env.perc(attT, relT * 1.5, amod, curve: \lin).kr;

    osc4 = SinOsc.ar(freq) * 6.7341546494171 * fxiii * env4;
    osc3 = SinOsc.ar(freq * 2, osc4) * env3;
    osc2 = SinOsc.ar(freq * 30) * 0.683729941 * env2;
    osc1 = SinOsc.ar(freq * 2, osc2) * env1;
    snd = Mix((osc3 * (1 - fxiv)) + (osc1 * fxiv));
  	snd = snd * (SinOsc.ar(fxi).range((1 - fxii), 1));

    snd = snd * Env.asr(0, 1, 0.1).kr(gate: gate, doneAction: Done.freeSelf);
    snd = Pan2.ar(snd, pan, amp);

    Out.ar(out, snd)})



SynthDef.new("organReed", {|amp=1,freq=440,gate=1,out=0,pan=0,
    attT = 0.3, relT = 0.3,
    //Depth and Rate Controls (fxiii and fxiv range from 0 to 1)
    fxi = 0.04, fxii = 0.06, fxiii = 0.1, fxiv = 0.05, fxv = 5,
    //Other Controls
    fxvi = 18000, fxvii = 0.82, fxviii = 2442, rq = 0.3, fxxi = 1200, fxx = 1, fxxii = 1|

    var snd, env;

    // The same envelope controls both the resonant freq and the amplitude
    env = Env.asr(
        attackTime: attT,
        sustainLevel: amp,
        releaseTime: relT).ar(gate: gate, doneAction: Done.freeSelf);

    // pulse with modulating width
    snd = Pulse.ar(
        freq: TRand.ar(lo: 2.pow(-1 * fxi), hi: 2.pow(fxi), trig: gate) * freq,
        width: LFNoise1.kr(freq: fxii, mul: fxiii).range(0, 1),
        mul: 0.0625);  //Incereasing this lessens the impact of the BPF

    // add a little "grit" to the reed
    //original used snd = Disintegrator.ar(snd, 0.5, 0.7);
    snd = Latch.ar(snd, Impulse.ar(fxvi * 2));

    // a little ebb and flow in volume
    snd = snd * LFNoise2.kr(freq: fxv).range((1 - fxiv), 1);

    //Filtering (BHiShelf intensifies the buzzing)
    snd = snd + BPF.ar(in: snd, freq: env.linexp(0, amp, fxviii * fxvii, fxviii), rq: rq);
    snd = BHiShelf.ar(in: snd, freq: fxxi, rs: fxx, db: fxxii);

    //Output
    snd = Mix.ar(snd * env);

    Out.ar(out, Pan2.ar(snd, pan))})


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

SynthDef.new("karp",{|amp=1,freq=440,gate=1,out=0,pan=0,
    susT=1, fmod=0, rate=22, blur=1, fxi=0.666|
    var osc, env;
    susT = susT * blur;
    freq = [freq, freq+fmod];
    amp=(amp * 0.4);
    osc=LFNoise0.ar((400 + (400 * rate)), amp);
    osc=(osc * XLine.ar(1, 1e-06, (susT * 0.1)));
    freq=((265 / (freq * fxi)) * 0.005);
    osc=CombL.ar(osc, delaytime: freq, maxdelaytime: 2);
    env=EnvGen.ar(Env(times: [susT],levels: [(amp * 1), (amp * 1)],curve: 'step'), doneAction: Done.freeSelf);
    osc=(osc * env);
    osc = Mix(osc) * 0.5;
    osc = Pan2.ar(osc, pan);
	Out.ar(out, osc)})

SynthDef.new("arpy",{|amp=1,freq=440,gate=1,out=0,pan=0,
    susT=1, fmod=0, blur=1, cut=3000|
    var osc, env;
    susT = susT * blur;
    freq = [freq, freq+fmod];
    freq=(freq / 2);
    amp=(amp * 2);
    freq=(freq + [0, 0.5]);
    osc=LPF.ar(Impulse.ar(freq), cut);
    env=EnvGen.ar(Env.perc(attackTime: 0.01, releaseTime: susT * 0.25, level: amp, curve: 0), doneAction: Done.freeSelf);
    osc=(osc * env);
    osc = Mix(osc) * 0.5;
    osc = Pan2.ar(osc, pan);
	Out.ar(out, osc)})

SynthDef.new("prophet",{|amp=1,freq=440,gate=1,out=0,pan=0,
    susT=0.1,
	lfoS=1, lfoD=0.5, cut=6000, fxi=0.4, fxii=1.01|

    var lfo, pulse, filter, env;
    amp = amp * 0.1;

    lfo = LFTri.kr(lfoS * [1, fxii], Rand(0, 2.0)!2);

    pulse = Pulse.ar(freq * [1, fxii], lfo * lfoD + 0.5);

    filter = RLPF.ar(pulse, cut, fxi);

    filter = BHiPass.ar(filter, 200);

    env = EnvGen.ar(Env([0,1,0.8,0.8,0], [0.01, 0, susT, susT]), doneAction:Done.freeSelf);

    Out.ar(out, Pan2.ar(Mix(filter) * env * amp * 0.5, pan))})


SynthDef.new("jbass",
{|amp=1, susT=1, pan=0, freq=0, vib=0, fmod=0, rate=0, out=0,
blur=1, beat_dur=1, atk=0.01, decay=0.01, rel=0.01, peak=1, level=0.8|
    var osc, env;
    susT = susT * blur;
    freq = [freq, freq+fmod];
    freq=(freq / 4);
    amp=(amp * 0.8);
    osc=LFTri.ar(freq, mul: amp);
    env=EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), susT - (atk + decay + rel)), rel], curve:\sin), doneAction: 0);
    osc=(osc * env);
    osc = Mix(osc) * 0.5;
    osc = Pan2.ar(osc, pan);
	Out.ar(out, osc)})

SynthDef.new("ksBass", {|amp=1,freq=440,gate=1,out=0,pan=0,
	relT = 1.5,
    // Parameters for the impulse shape
	attT = 0.5, susT = 1, fxi = 0.5, fxii = 1,
	// Filter and compressor parameters, thresh goes from 0 to 1.
	cut = 250, filtermax = 5000, fxiii = 0.35, fxiv = 0.2, fxv = 2.5|

	var total, exciter, snd;

	// Rescale impulse values for the frequency of the note
	total = (attT + susT + fxi + fxii) * freq;

	// Initial impulse
	exciter = Env.new(
		levels: [0, 1, 1, 0, 0],
		times: [attT, susT, fxi, fxii]/total).ar;

	// Delay line
	snd = CombN.ar(
		in: exciter,
		maxdelaytime: 0.06,
		delaytime: 1/freq,
		decaytime: relT);

	// LPF
	snd = RLPF.ar(
		in: snd,
		freq: LinExp.ar(Amplitude.ar(in: snd), 0, 1, cut, filtermax),
		rq: fxiii);

	// Compressor for fun
	snd = CompanderD.ar(
		in: snd,
		thresh: fxiv,
		slopeBelow: 1,
		slopeAbove: 1/fxv);

	// Output stuff
	snd = Mix.ar(snd) * amp;
	snd = Limiter.ar(snd);

	DetectSilence.ar(in: snd, doneAction: Done.freeSelf);

    Out.ar(out, Pan2.ar(snd, pan))})




SynthDef.new("dBass", {|amp=1,freq=440,gate=1,out=0,pan=0,
	susT=1, fmod=0, rate=0, fxi=0.02|
		var osc, env;
		freq = [freq, freq+fmod] * Line.ar(Rand(0.5,1.5),1,fxi);
		amp=(amp * 0.1);
		osc=( VarSaw.ar(freq, width: LFTri.ar((0.5 * rate)/susT, iphase:0.9, add:0.8, mul: 0.2), mul: amp));
		env=EnvGen.ar(Env([0,1,0.8,0.8,0], [fxi, 0.01, susT/2, susT/2]), doneAction: Done.freeSelf);
		osc=(osc * env);
		osc = Mix(osc) * 0.5;
		osc = Pan2.ar(osc, pan);
		Out.ar(out, osc)})


SynthDef.new("gritBass", {|
	//Blend goes from 0 to 1
	out = 0, amp = 0.5, pan = 0, freq = 440, att = 0.001, rel = 1, curve = 8, blend = 0.5|

    var env, in, ina, synca, octa, inb, syncb, octb, octave, snd;

	//A slightly rounded percussive envelope
	env = Env.perc(att, rel, amp, [curve, -1 * curve]).kr(doneAction: 2);

	/*  Input wave +/- 90 degrees - To use SinOsc.ar, replace:
	        -"iphase:  0" with "phase: pi/2"
	        -"iphase:  1" with "phase: 0"
	        -"iphase: -1" with "phase: pi"   */
	in = LFPar.ar(freq: freq * 2, iphase: 0);
	ina = LFPar.ar(freq: freq * 2, iphase: 1);
	inb = LFPar.ar(freq: freq * 2, iphase: -1);

	//Two square waves exactly out of phase and an octave below the input wave
	synca = LFPulse.ar(freq: freq, iphase: 0);
	syncb = LFPulse.ar(freq: freq, iphase: 0.5);

	//This smoothly swaps between outputting the +90 degree wave and -90 degree wave
	octa = ina * synca;
	octb = inb * syncb;
	octave = Mix.ar([octa, octb]);

	//Mixer stage, volume adjustments, envelope, and output
	snd = Mix.ar([octave * blend, in * (blend - 1)]);
    snd = LeakDC.ar(snd);
	snd = Limiter.ar(in: snd, level: 1);
	snd = snd * env;


	Out.ar(out, Pan2.ar(snd, pan));
})

SynthDef.new("oc2bass", {|
	//Blend goes from 0 to 1
	out = 0, amp = 0.5, pan = 0, freq = 440, att = 0.001, rel = 0.15, curve = -8, blend = 0.5|

        var env, in, ina, synca, octa, inb, syncb, octb, octave, snd;

        //A slightly rounded percussive envelope
        env = Env.perc(att, rel, amp, [curve, -1 * curve]).kr(doneAction: 2);

        //Input wave - To use SinOsc.ar, replace "iphase: 2" with "phase: 3pi/2"
        in = LFPar.ar(freq: freq * 2, iphase: 2);

        //Mirroring the wave around the x-axis
        ina = in.range(0, 1);
        inb = ina * -1;

        //Two square waves exactly out of phase and an octave below the input wave
        synca = LFPulse.ar(freq: freq, iphase: 0);
        syncb = LFPulse.ar(freq: freq, iphase: 0.5);

        //This smoothly swaps between outputting the input wave and its mirror
        octa = ina * synca;
        octb = inb * syncb;
        octave = Mix.ar([octa, octb]);

        //Mixer stage, volume adjustments, envelope, and output
        snd = Mix.ar([octave * blend * 0.5, in * (1 - blend) * 0.25]);
        snd = LeakDC.ar(snd);
        snd = Limiter.ar(in: snd, level: 1);
        snd = snd * env;

        Out.ar(out, Pan2.ar(snd, pan));
})


SynthDef.new("feedbackPad", {|amp=1,freq=440,gate=1,out=0,pan=0,
	// Envelope Controls
	attT = 3, decT = 1, susL = 1, relT = 5,
    fxi = 0,
	// Other Controls (interval is in semitones)
	fxii = 2, fxiii = 3, fxiv = 14|

	var env, fbIn, snd;

	// Set up the Envelopes
	env = Env.adsr(
		attackTime: attT,
		decayTime: decT,
		sustainLevel: susL,
		releaseTime: relT,
		curve: fxi).ar(gate: gate);

	// Receive and Sample the feedback
	fbIn = Latch.ar(
		in: (LocalIn.ar + 1)/2,
		trig: Impulse.ar(
			freq: fxii));
	fbIn = (fbIn * fxiii.abs * env).round(1);
	fbIn = (fbIn * fxiv).midiratio;

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




SynthDef.new("aPad", {|amp=1,freq=440,gate=1,out=0,pan=0,
	//Standard Values:
	attT = 0.4, decT = 0.5, susL = 0.8, relT = 1.0,
	//Other Controls:
	fxi = 4, fxii = 0.015, fxiii = 5,
	//These controls go from 0 to 1:
	tremoloDepth = 0.5|

	var env, snd, vibrato, tremolo, mod2, mod3;

    freq = freq.lag(0.05);

    amp = amp * 0.1;

	env = Env.adsr(attT, decT, susL, relT).kr(gate: gate);
	vibrato = SinOsc.kr(fxi).range(freq * (1 - fxii), freq * (1 + fxii));
	tremolo = LFNoise2.kr(1).range(0.2, 1) * SinOsc.kr(fxiii).range((1 - fxii), 1);

	snd = SinOsc.ar(freq: [freq, vibrato], mul:(env * tremolo * amp)).distort;
	snd = Mix.ar([snd]);

	DetectSilence.ar(snd, 0.0001, 0.2, doneAction: Done.freeSelf);
	Out.ar(out, Pan2.ar(snd, pan))})




SynthDef.new("moogBass", {|amp=1,freq=440,gate=1,out=0,pan=0,
    attT=0.001,decL=0.3,susT=0.9,relT=0.2
	cut=1000, amod=2.0, prt=0.01, fxi=0.7|

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
		freq: cut * (1.0 + (0.5 * filterenv)),
		gain: amod);

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

	snd = snd + (chorusfx * fxi);

	Out.ar(out, Pan2.ar(snd, pan))})



SynthDef.new("samplerALT", { |out = 0, start = 0, susT = 15, amp = 1, rate = 1, buf = 0, pan = 0, ofs=0.0,
        relT=0.05, lfoS=440, lfoD=0.0|
    var osc, env;

    // TODO: LFO on rate that isn't terror

    osc = PlayBuf.ar(1, buf, BufRateScale.kr(buf) * rate, startPos: start);
    amp = amp * 2.0; // I have found that sample amp usually lands way lower than any synth amp
    osc = osc * EnvGen.ar(Env([0,1 * amp,1 * amp,0],[ofs, susT-0.05, relT]), doneAction: Done.freeSelf);
    osc = Mix(osc);
    osc = Pan2.ar(osc, pan);

	Out.ar(out, osc)})



// Effects below

SynthDef.new("router",
    {|in=0,out=0|
    Out.ar(out,In.ar(in,2))})




SynthDef.new("clamp",
    {|out=0, over=0, under=9000, mul=1.0, add=0.0, modBus=100|
    var snd, mod;
    mod = In.kr(modBus, 1);
    snd = In.ar(out,2);
    snd = HPF.ar(in: snd, freq: over, mul: mul, add: add);
    snd = LPF.ar(in: snd, freq: under + mod, mul: mul, add: add);
    ReplaceOut.ar(out,snd)})



SynthDef.new("delay", {|out=0, echo=0.25, beat_dur=1, echt=1.0|
var osc;
osc = In.ar(out, 2);
osc = osc + CombL.ar(osc, delaytime: echo * beat_dur, maxdelaytime: 2 * beat_dur, decaytime: echt * beat_dur);
ReplaceOut.ar(out, osc)})



SynthDef.new("controlMod", {|value=0, out=0, prt=0|

    value = value.lag(prt);
    Out.kr(out, value)})


SynthDef.new("compressor", {|out=0, drive=0.5, mul=1, add=0, thr=0.5, slp=1, att=0.01,rel=0.1|
    var osc;
    osc = In.ar(out, 2);

    osc = Compander.ar(
        in: osc, 
        control: osc, 
        thresh: thr, 
        slopeBelow: 1.0, 
        slopeAbove: 1.0 / slp, 
        clampTime: att, 
        relaxTime: rel, 
        mul: mul, 
        add: add);

    ReplaceOut.ar(out, osc)})


SynthDef.new("tube", {|out=0, drive=0.5|
    var osc;
    osc = In.ar(out, 2);
    // TODO 
    //osc = TwoTube.ar(input: osc, k: 0.01, loss: 1.0, d1length: 100, d2length: 100, mul: 1.0, add: 0.0);
    ReplaceOut.ar(out, osc)})

SynthDef.new("distortion", {|out=0, drive=0.5|
    var osc;
    osc = In.ar(out, 2);
    osc = (osc * (drive * 50)).clip(0,0.2).fold2(2);
    ReplaceOut.ar(out, osc)})



SynthDef.new("analogTape", {|out=0,bias=0.8,sat=0.8,drive=0.2,ovr=1|
    var snd;
    snd = In.ar(out,2);

    //snd = VarSaw.ar(440.0, width: 0.5);
    snd = AnalogTape.ar(snd, bias: bias, saturation: sat, drive: drive, oversample: ovr, mode: 0);

    ReplaceOut.ar(out, snd)})


SynthDef.new("analogChew", {|out=0|
    var snd;
    snd = In.ar(out,2);

    //snd = snd + VarSaw.ar(440.0, width: 0.5);
    snd = AnalogChew.ar(snd);

    ReplaceOut.ar(out, snd)})



SynthDef.new("reverb",
    {|amp=1, out=0, room=0.7, mix=0.33, damp=0.5,mul=1.0,add=0.0|
    var snd;
    snd = In.ar(out,2);
    snd = FreeVerb.ar(snd, mix: mix, room: room, damp: damp, mul: mul, add: add);
    ReplaceOut.ar(out,snd)})
