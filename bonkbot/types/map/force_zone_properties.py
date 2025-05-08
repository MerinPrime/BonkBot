from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .force_zone_type import ForceZoneType


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IBodyForceZoneProperties.ts
@dataclass
class ForceZoneProperties:
    enabled: bool
    type: 'ForceZoneType'
    x_force: float
    y_force: float
    push_players: bool
    push_bodies: bool
    push_arrows: bool
    center_force: float
