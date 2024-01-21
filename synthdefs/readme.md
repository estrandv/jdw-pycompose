# Synthdefs that can be sent to jdw-sc

- Since the /read_scd osc message is available, we can define synths here instead of in jdw-sc
- An annoying shortcoming of this appraoch is that NRT recording won't know about the synths we send with .add; 
    - You can technically bake these templates into the NRT-record message as well, but it's still pretty convoluted 
- The biggest gain is of course that you get to experiment in real time with new defs 