from enum import Enum
from re import M
class Gender(Enum):
    M = 1
    F = 2
    NONE = 3

    def get_enum(value):
        if value == "m":
            return Gender(Gender.M)
        elif value == "f":
            return Gender(Gender.F)
        else:
            return Gender(Gender.NONE)
    
    def get_caption(value):
        if value == Gender(Gender.M):
            return "m"
        elif value ==  Gender(Gender.F):
            return "f"
        else:
            return Gender(Gender.NONE)