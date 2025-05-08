from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bonkbot.types.map.capture_type import CaptureType


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/ICapZone.ts
@dataclass
class CapZone:
    name: str
    shape_id: int
    seconds: float
    type: 'CaptureType'
