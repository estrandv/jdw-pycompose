from zmq_client import PublisherClient

def effect_base(target: str, inBus: int, outBus: int):
    return {"target": target, "args": {"inBus": float(inBus), "outBus": float(outBus)}}

class EffectChain:
    def __init__(self, start_bus = 17):
        self.effects: list[dict] = []
        self.current_bus = start_bus

    def reverb(self, out_bus: int, room=0.5, mix=0.5):
        eff = effect_base("effect_reverb", self.current_bus, out_bus)
        self.effects.append(eff)
        self.current_bus = out_bus
        eff["args"]["room"] = room 
        eff["args"]["mix"] = mix
        return self 

    def distortion(self, out_bus: int, amount = 0.18):
        eff = effect_base("effect_distortion", self.current_bus, out_bus)
        self.effects.append(eff)
        self.current_bus = out_bus
        eff["args"]["dist"] = amount
        return self   

    def comb_delay(self, out_bus: int, echo = 0.2, beat_dur = 1.0, echotime = 0.5):
        eff = effect_base("effect_combDelay", self.current_bus, out_bus)
        self.effects.append(eff)
        self.current_bus = out_bus
        eff["args"]["echo"] = echo  
        eff["args"]["beat_dur"] = beat_dur  
        eff["args"]["echotime"] = echotime
        return self 

    def bit_crush(self, out_bus: int, bits=4.0, crush=1.0):
        eff = effect_base("effect_bitCrush", self.current_bus, out_bus)
        self.effects.append(eff)
        self.current_bus = out_bus
        eff["args"]["crush"] = crush   
        eff["args"]["bits"] = bits  
        return self 

    def limiter(self, out_bus: int, level=1.0):
        eff = effect_base("effect_limiter", self.current_bus, out_bus)
        self.effects.append(eff)
        self.current_bus = out_bus
        eff["args"]["level"] = level
        return self 

    def bandpass(self, out_bus: int, bpf=1200.0, bpr=0.04, bpnoise=0.2, sus=1.0):
        eff = effect_base("effect_bandPass", self.current_bus, out_bus)
        self.effects.append(eff)
        self.current_bus = out_bus
        eff["args"]["bpf"] = bpf
        eff["args"]["bpr"] = bpr
        eff["args"]["bpnoise"] = bpnoise
        eff["args"]["sus"] = sus
        return self 

    def filterswell(self, out_bus: int, swell = 1.0, sus = 1.0, hpr = 1.0):
        eff = effect_base("effect_filterSwell", self.current_bus, out_bus)
        self.effects.append(eff)
        self.current_bus = out_bus
        eff["args"]["swell"] = swell
        eff["args"]["sus"] = sus
        eff["args"]["hpr"] = hpr
        return self 


    def debug(self):
        print([effect for effect in self.effects])
        return self 

    def send(self, client: PublisherClient):
        # For some reason the effect chain must be built in reverse for supercollider to respond
        ordered = self.effects
        ordered.reverse()
        for eff in ordered:
            client.add_effect([eff])