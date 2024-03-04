SynthDef("pycompose",
{|amp=1, sus=0.2, pan=0, bus=0, freq=440, cutoff=1000, rq=0.5, fmod=1, relT=0.04, fxa=1.0, fxf=300, fxs=0.002|
	var osc1, osc2, filter, filter2, env, filterenv, ab;
	amp = amp * 0.2;
	freq = freq * fmod; 
	
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
}).add; 

SynthDef("filtersquare",
{|amp=1, sus=0.2, pan=0, bus=0, freq=440, cutoff=500, rq=0.5, fmod=1, relT=0.04, fxa=1.0, fxf=300, fxs=0.002, gate=1|
	var osc1, osc2, filter, filter2, env, filterenv, ab, snd, adsrvol, lowpass;
	amp = amp * 0.5;
	freq = freq * fmod; 
	
	// Note the chaining of oscs 
	osc1 = Pulse.ar(freq) + Saw.ar(freq * 1.008) + (Saw.ar(freq * 2) * 0.8);

	// Applied with * 
	adsrvol = EnvGen.ar(Env.adsr(2.1, 0.8, 0.6, relT), gate, doneAction:Done.freeSelf);

	// Applied through replacement - note the * for cutoff and envgen 
	// Note that filters are a bit strange and might want to freeself? 
	lowpass = RLPF.ar(osc1, cutoff * EnvGen.ar(Env.adsr(0.2, 0.6, 0.5, relT / 2), gate, doneAction:Done.freeSelf), rq);

	snd = lowpass * adsrvol * amp;

	snd = Pan2.ar(snd, pan);

	snd = AnalogTape.ar(snd);

	Out.ar(bus,snd)
}).add; 

SynthDef("eli",
{|amp=1, sus=0.2, pan=0, bus=0, freq=440, gate=1, lfoS=3220, lfoD=4, cut=500, fx=0.2|
	var osc1, modulator, snd, adsrvol, lowpass;
	amp = amp * 0.5; 
	
	// Mul is the breath of the oscillations
	// Still not really behaving like I expect lfoS/D to work...  
	// "Modulator freq determines sideband spacing, modulator mul determines number of audible sidebands"
	// Eli uses more like lfoD=400 but that sounds off to me - seems to work better with SinOsc main  
	modulator = SinOsc.ar(freq, mul: lfoD);

	// Eli Fieldsteel on YouTube denotes this as "number of sidebands increating as mul goes up"
	// Another tutorial noted that sidebands are what denote a complex sound, such as a piano 
	osc1 = Pulse.ar(freq + modulator);
	
	osc1 = osc1 + (Saw.ar(freq * 4) * fx); // Saw adds an edge, can be removed 
	osc1 = osc1 + (Pulse.ar(freq * 8) * fx); // Pulse adds a bright ring, more toypiano-esque  

	// Applied with * 
	adsrvol = EnvGen.ar(Env.adsr(0.0, 0.8, 0.6, 2.4), gate, doneAction:Done.freeSelf);

	// Applied through replacement - note the * for cutoff and envgen 
	// Note that filters are a bit strange and might want to freeself?
	// Note that LPF cutoff is the "maximum allowed frequency", which might mean that the adsr 0.x values makes it MORE strict 
	lowpass = RLPF.ar(osc1, cut * EnvGen.ar(Env.adsr(0.0, 0.7, 0.3, 0.2), gate, doneAction:Done.none), 0.5);

	snd = lowpass * adsrvol * amp * 1.0;

	snd = Pan2.ar(snd, pan);

	Out.ar(bus,snd)
}).add; 

SynthDef("elisin",
{|amp=1, sus=0.2, pan=0, bus=0, freq=440, gate=1, lfoD=1633, cut=500|
	var osc1, modulator, snd, adsrvol, lowpass, mod2;
	amp = amp * 0.5; 
	
	modulator = SinOsc.ar(freq, mul: lfoD);
	osc1 = SinOsc.ar((freq * 4) + modulator);
	
	osc1 = osc1; // + (Pulse.ar(freq) * 4);

	// Applied with * 
	adsrvol = EnvGen.ar(Env.adsr(0.2, 1.0, 0.8, 2.4), gate, doneAction:Done.freeSelf);

	osc1 = osc1 + (Saw.ar(freq * 1.008) * 1); // Some attempt at a detune, sounds pretty neat 

	// Applied through replacement - note the * for cutoff and envgen 
	// Note that filters are a bit strange and might want to freeself?
	// Note that LPF cutoff is the "maximum allowed frequency", which might mean that the adsr 0.x values makes it MORE strict 
	lowpass = RLPF.ar(osc1, cut * EnvGen.ar(Env.adsr(0.2, 2.8, 0.4, 2.2), gate, doneAction:Done.none), 0.5);

	snd = lowpass * adsrvol * amp * 1.0;

	snd = Pan2.ar(snd, pan);

	Out.ar(bus,snd)
}).add; 
