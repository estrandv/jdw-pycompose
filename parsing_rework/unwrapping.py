"""

	#### NEW TAKES 

Recursiveness becomes tricky as soon as we require state and would require additional utility objects.

Still, I think it would be the cleanest. 

The core issue is this: each alternation, on each level, should have its own counter.

The counter should be the modulo; a "get next looping" for the alternation set. 

This should trigger individually each time that particular alternation is "selected". 

So we still start with getting the minimum required iterations and looping that. 

But instead of passing the modulo as the iteration variable, we call getNext each step along the way. 

Q: Is it possible to do getNext(element) and keep a state outside? 
	- The python "is" operator checks if two object references point to the same place in memory. 
	- It should be possible to do some form of array magic here  




	#### BELOW IS OLD TALK 



	TODO: Unwrapping alternation sections 

	General note: Probably the last thing we want to do, after atomic string parsing. 

	1. Detect the minimum number of full-set iteration required to expand all alternations 

		g (a / b (c / d))

		=> g a g b c g a g b d
		=> 4 repeats 

		top level has zero alternations (is not alternating) 
		
		second level has two alternations

		third level has two alternations 

		if each layer has a multiplier, it is 2 * 2 * 1 = 4 

		g (a / (b / c) / (d / e))
		 
		g a g b g d g a g c g e

		1 * 3 * 2 * 2 = 12 

		should be: 6 

		For each level, we only account for the alternation with the highest number 

		So the value of any given level is: 
		
			The amount of elements times the highest value contained in the elements 

			mylen: 
				(len(elements) OR 1 if not alternation) * find_highest(elements)

			find highest will have some recursive action by again calling mylen on the nested elements  

	2. Expand recursively, starting with a loop of this number from the top level 

		So if we walk from zero to the max:

		full_set = [] 

		for i in range(0, max):
			full_set += expand(i)

		expand(i):
			if atom: return [atom]
			if regular: return flat[e.expand(i) for e in elements] 
			if alt: return elements[i % len].expand(i)

	3. Things to bear in mind 

		a) Sections can be repeated. This is probably best done before expansion begins. 

		So: (a b c (a d / f)x3)

		should first become (a b c (ad/f) (ad/f) (ad/f))

		which can then be expanded using the regular rules 

		I hope 

		
		b) We've yet to account for shared args and all that

		But I think that can be done just as well before as after this 


		c) Object format 
		
		Expansion should not care what is contained in each section. As such, the parsed string sections from parsing would do just fine. 

		Ideally, a repeated atomic object should of course only have to be parsed once. 

		In practice, however, it feels neater to reuse the same section objects where we can. 

		Optimization can just as easily be via maps. 

	CONCLUSION: 

		We can reuse the section objects from parsing to expand. 

		If section repetition is supported, it should be done before expansion. 
	

"""
