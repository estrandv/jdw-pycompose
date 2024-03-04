# Rethinking the atomic parts 


c4[=1 >1 #1] -> MessageDefinition(prefix, index, suffix, varargs) -> TimedOsc<NoteOnTimedMessage>
	-> Infers synth_name and sampling behaviour from meta-context 
	-> Implication: Always expect MessageDefinition to be the end result of a parse string
	-> Ideally, the parse string should result in an interface that produces TimedOsc regardless of contents
		... including but not limited to MD ... 

{} = Section split 
	-> Basically implies that the string is many separate parseable strings
	-> Allows for repeat with the x-syntax 
	-> Shared :: default args from the full string (should kinda work recursively, too, in theory)

Consider messages within messages: 

c2 c3 c4 -> Arr<MD> -> Arr<TimedOsc> -> QueueMsg<...> -> saveAndTag(:myMsg} 

d3 d3 {:myMsg =1} -> parseAtomic() -> return Arr of MD OR MessageReference(name, resTime) which in to_osc produces the saved message

# Brainstorming other args syntaxes 

f3:>1#1=1relT0.2 -> Spaces are not required, thus brackets are not required (but readability is hurt)

f3:sus0.2,relT0.4,#1,=1 -> Better

d3id:x3,b55 f3@id:>0.2 -> Mod id syntax would have to change slightly

# The slash syntax 

Very helpful and generally intuitive, but has an awkward relationship with master args and sections. 

Parentheses are also awkward to type. 

c3 d4 | e3:sus0.2,#2 / f3 | d3 a4 -> Generally more comfortable but does not allow nesting

c3 (c3/(c4/d4))

c3 | c3 / | c4 / d4 | -> One alternative that takes a bit of clever parsing 

c3 c3/c4//d4 -> Deep nesting. Also a challenge but both readable and easy. 

It does however ruin space behaviour for more advanced alternations. 

c3 d3/d4 |8  c3 c3 | -> number tagging can replace the x-tag but is less readable. 

Intuitively you want slashes to resolve on full iteration repeats rather than individually.

This can be done by saving slashes as array structures on parsing before a second iteration: 

c3 d3/d4//d5 -> [c3 [d3 [d4 d5]]]

It's worth considering if () should just always imply alternations, removing the need for slashes altogether: 

c3 (d3 (d4 d5))

But, again, this creates issues when distinguishing alternations vs parts of alternated sequences: 

c3 (d3 [d4 d5]) -> [c3 [d3 [d4 d5]]]
c3 (d3 (d4 d5)) -> [c3 [d3 [[d4] [d5]]]]?? 

And what about sectioning? 

c3 | (a3 d3 | a4 (d4 e4)) -> Is this illegal? Or what should it mean?

What is a section? 

"A section is a list of notes that can be repeated or appended with common args"

A section should not affect alternations, ideally. Maybe. 

a3 a3 b3 f3 a3 a3 b3 g3:0.5 f3:0.5 -> Say you want to write this. 

a3 |2 b3 | f3 / g3:0.5 f3:0.5  -> Kinda works? 

a3 | f3 / d3 g3 // a5 -> I think this kinda works too? 

So you would iterate like:

	We keep an array of atoms.

	If we come across "/", we make a nested array of atoms. 

	If we come across "|", we wrap the section of the top level atom arrays so far. 

	And then of course all that hoohaa with being in different modes and knowing what to expect/forbid. 

	Bearing in mind the meta message templating syntax and expectation. 

This can be rewritten in python or as a command line util that spits out json for python to make osc out of. 

Closing note: The TIME arg is its own sacred thing and can probably be implied as "C4:0.5,>0.6"

# Revisited, again 

Going again on the core idea of the section (repetition), it should not be used to denote the starting 
	point of an alternation sequence. 

c3 d4 | a4 / f5 | e4 c4 |3 -> Or is it fine? These things are hard to parse in your head. 

c3 | d5 / | a2 |8 -> This is a good example, I guess. Repeat a2 eight times every other iteration. 
	Even weirder if you want d5 to be the repeating pattern. 

c3 % | d5 a5 |8 / | d4 | a5 // f5 |8 % -> Nested also gets a bit nasty with this. 

To avoid going fully into the old ()-way, you can of course fall back on that with single-symbol: 

c3 % d5 a5 / d4 % a5 / f5 %% -> But by then, parenthesis is already infinitely more readable.   

So we might want to keep parentheses, but we need to be consistent with the usage: 

(c3)*8 ( d5 d6 / ( _ / a5) d7 )*3:0.5,#2 -> This is a section, innit?  

Sad thing is that it REALLY is more annoying to write this way.

So we're back to thinking about sections and alternations as joined concepts. 

c3 § d5 d6 / § _ / a5 d7 §§ -> Example of needing to close the whole thing, which is the main difference.

... but how does the parser know if we're closing the old level or opening a new one? Lol. 

I guess it can infer it from "//" or something but by now we're pretty deep into the water. 

So we can't escape the humble parenthesis. 

And with that in mind we should probably ditch the master arg as well, convenient for the fingers as it is. 

Another notable thing is that if a ()-section behaves as an "apply all", then there is no need to have "*" be unique for that: 

( c3lol*3:.5 ( c4:#0.8 c4 )*3 ):.25#1,>1

x = Name as x
@x = Modify named as x 
*n = Repeat n times
: = Args begin 

Note that we have to be careful to preserve the convenient old parsing divide: 

Prefix: text before the first number (any)
Index: First consecutive integer
Suffix: Non-symbol letters immediately following the index
Symbols: <Symbol, string> map of known symbols and their non-whitespace following text before next space 
... and then the question is if ARGS is a symbol too or if we treat it differently due to being last ... 

BONUS NOTE: ".25" shorthand for "0.25" should be applied and is as simple as appending "0" to parsed floats that start with ".". 
BONUS NOTE #2: Relargs would be neatest as operators: "c4:#+.25", "d5:#*2,>.25". 
	-> Lets each arg dictate what class it is
	-> Makes it easy to remember what different operators do
	-> Is compatible with other "*" usage, but can still use another symbol for clarity  









