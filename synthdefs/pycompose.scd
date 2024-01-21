SynthDef("pycompose",
{|amp=1, sus=0.2, pan=0, bus=0, freq=440, cutoff=1000, rq=0.5, fmod=0, relT=0.04, fxa=1.0, fxf=300, fxs=0.002|
	var osc1, osc2, filter, filter2, env, filterenv, ab;
	amp = amp * 0.2;
	
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