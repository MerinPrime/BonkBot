from dataclasses import dataclass
from typing import Optional


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IMapProperties.ts
@dataclass
class MapProperties:
    grid_size: float = 25
    players_dont_collide: bool = False
    respawn_on_death: bool = False
    players_can_fly: bool = False
    complex_physics: bool = False
    a1: Optional[bool] = True
    a2: Optional[bool] = False
    a3: Optional[bool] = False
