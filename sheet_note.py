from copy import deepcopy
from decimal import Decimal

class SheetNote:
    def __init__(self, prefix: str, suffix: str, tone_value: float, \
        master_args: dict[str, float], base_args: dict[str, float], rel_args: dict[str, list[float]] = {}, mul_args = {}):
        
        self.prefix = prefix
        self.suffix = suffix
        self.tone_value = tone_value
        self.master_args = master_args
        self.base_args = base_args
        self.relative_args: dict[str, list[float]] = rel_args # Arg values added to the final values 
        self.mul_args: dict[str, float] = mul_args # Arg multipliers for the final values

    def __deepcopy__(self, memo):
        return SheetNote(
            self.prefix, 
            self.suffix, 
            self.tone_value, 
            dict(self.master_args), 
            dict(self.base_args), 
            dict(self.relative_args), 
            dict(self.mul_args)
        )

    def get_args(self):
        merged = dict(self.base_args)
        for attr in self.master_args:
            merged[attr] = self.master_args[attr]
        
        if self.relative_args:
            for attr in self.relative_args:
                for value in self.relative_args[attr]:
                    current = merged[attr] if attr in merged else 0.0
                    merged[attr] = current + value

        for attr in self.mul_args:
            merged[attr] = merged[attr] * self.mul_args[attr]

        # Perform rounding to limit python float drift 
        for attr in merged:
            merged[attr] = round(merged[attr], 5)

        return merged

    def set_mul(self, arg: str, value: float):
        self.mul_args[arg] = value 

    def set_relative(self, arg: str, value: float):
        if arg not in self.relative_args:
            self.relative_args[arg] = []
        self.relative_args[arg].append(value)

    def set_arg(self, arg: str, value: float):
        self.base_args[arg] = value

    def set_master_arg(self, arg: str, value: float):
        self.master_args[arg] = value

    def get_time(self):
        return self.get_args()["time"] if "time" in self.get_args() else 0.0

    def get_tone_in_oct(self, octave: int) -> float:
        extra = (12 * (octave + 1)) if octave > 0 else 0
        return self.tone_value + extra
