# Moving towards a billboarding lib
- We can easily just make one that exposes parse_billboard and nothing else
  - This could of course later separate its helper dependencies into a more general lib if needed
- Some things to keep in mind
  - Hardcodes, such as "DELAY", should probably not be in the lib
  - synthDefs and sample reading are also more part of how a song is defined
