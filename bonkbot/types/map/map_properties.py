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
    a1: Optional[bool] = None
    a2: Optional[bool] = None
    a3: Optional[bool] = None

    @staticmethod
    def from_json(data: dict) -> 'MapProperties':
        properties = MapProperties()
        properties.grid_size = data.get('gd', 25)
        properties.players_dont_collide = data.get('nc', False)
        properties.respawn_on_death = data.get('re', False)
        properties.players_can_fly = data.get('fl', False)
        properties.complex_physics = data.get('pq', 1) == 2
        properties.a1 = data.get('a1')
        properties.a2 = data.get('a2')
        properties.a3 = data.get('a3')
        return properties
