import enum
from dataclasses import dataclass


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
    enabled: bool
    type: 'ForceZoneType'
    x_force: float
    y_force: float
    push_players: bool
    push_bodies: bool
    push_arrows: bool
    center_force: float
