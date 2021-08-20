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

    def send(self, client: PublisherClient):
        client.add_effect(self.effects)