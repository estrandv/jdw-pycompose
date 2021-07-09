from copy import deepcopy

class SheetNote:
    def __init__(self, prefix: str, suffix: str, tone_value: float, master_args: dict[str, float], base_args: dict[str, float]):
        self.prefix = prefix
        self.suffix = suffix
        self.tone_value = tone_value
        self.master_args = master_args
        self.base_args = base_args

    def get_args(self):
        merged = deepcopy(self.base_args)
        for attr in self.master_args:
            merged[attr] = self.master_args[attr]
        return merged

    def set_arg(self, arg: str, value: float):
        self.base_args[arg] = value

    def get_time(self):
        return self.get_args()["time"] if "time" in self.get_args() else 0.0

    def get_tone_in_oct(self, octave: int) -> float:
        extra = (12 * (octave + 1)) if octave > 0 else 0
        return self.tone_value + extra
