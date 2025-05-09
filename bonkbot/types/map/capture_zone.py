import enum
from dataclasses import dataclass


class CaptureType(enum.IntEnum):
    NORMAL = 0
    INSTANT_RED = 1
    INSTANT_BLUE = 2
    INSTANT_GREEN = 3
    INSTANT_YELLOW = 4

    @staticmethod
    def from_id(type_id: int) -> 'CaptureType':
        for capture_type in CaptureType:
            if type_id == capture_type.value:
                return capture_type


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/ICapZone.ts
@dataclass
class CaptureZone:
    name: str
    shape_id: int
    seconds: float
    type: 'CaptureType'
