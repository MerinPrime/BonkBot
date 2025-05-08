from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    pass


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IMapProperties.ts
@dataclass
class MapProperties:
    grid_size: int
    players_dont_collide: bool
    respawn_on_death: bool
    players_can_fly: bool
    complex_physics: bool
    a1: Optional[bool]
    a2: Optional[bool]
    a3: Optional[bool]
