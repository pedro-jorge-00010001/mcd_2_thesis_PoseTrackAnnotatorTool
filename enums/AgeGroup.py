from enum import Enum

class AgeGroup(Enum):
    CHILD = 1
    YOUNG = 2
    ADULT = 3
    SENIOR = 4
    NONE = 0
   
    def get_enum(value):
        if value == "00-14(Child)":
            return AgeGroup(AgeGroup.CHILD)
        elif value == "15-24(Young)":
            return AgeGroup(AgeGroup.YOUNG)
        elif value == "25-64(Adult)":
            return AgeGroup(AgeGroup.ADULT)
        elif value == "65+(Senior)" :
            return AgeGroup(AgeGroup.SENIOR)
        else:
            return AgeGroup(AgeGroup.NONE)