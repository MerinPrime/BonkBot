import enum
from dataclasses import dataclass
from typing import Optional


class CaptureType(enum.IntEnum):
    NORMAL = 1
    INSTANT_RED = 2
    INSTANT_BLUE = 3
    INSTANT_GREEN = 4
    INSTANT_YELLOW = 5

    @staticmethod
    def from_id(type_id: int) -> 'CaptureType':
        for capture_type in CaptureType:
            if type_id == capture_type.value:
                return capture_type


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/ICapZone.ts
@dataclass
class CaptureZone:
    name: str = 'Cap Zone'
    shape_id: int = -1
    seconds: float = 10
    type: Optional['CaptureType'] = CaptureType.NORMAL
