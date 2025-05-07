from dataclasses import dataclass
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..mode import Mode


@dataclass
class MapProperties:
    grid_size: int = 25
    players_dont_collide: bool = False
    respawn_on_death: bool = False
    players_can_fly: bool = False
    complex_physics: bool = False
