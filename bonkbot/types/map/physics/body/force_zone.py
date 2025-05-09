import enum
from dataclasses import dataclass
from typing import Tuple


class ForceZoneType(enum.IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    CENTER_PUSH = 2
    CENTER_PULL = 3

    @staticmethod
    def from_id(type_id: int) -> 'ForceZoneType':
        for force_zone_type in ForceZoneType:
            if type_id == force_zone_type.value:
                return force_zone_type

# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IBodyForceZoneProperties.ts
@dataclass
class ForceZone:
    enabled: bool = False
    type: 'ForceZoneType' = ForceZoneType.ABSOLUTE
    # ABSOLUTE & RELATIVE
    force: Tuple[float, float] = (0, 0)
    # CENTER_PUSH & CENTER_PULL
    center_force: float = 0
    push_players: bool = True
    push_bodies: bool = True
    push_arrows: bool = True
