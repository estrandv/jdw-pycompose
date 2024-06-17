

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
    amp=(amp + 1e-05);
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
    amp=(amp + 1e-05);
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
    amp=(amp * 0.75);
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

SynthDef.new("distortion",
{|bus=0, drive=0.5|
var osc;
osc = In.ar(bus, 2);
osc = (osc * (drive * 50)).clip(0,0.2).fold2(2);
Out.ar(bus, osc)})




"""



def get() -> list[str]:
    synthdefs = split_stack.split("+++")
    return synthdefs