from dataclasses import dataclass

from ..collide import CollideFlag, CollideGroup
from .body_type import BodyType


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IBodyShape.ts
@dataclass
class BodyShape:
    body_type: 'BodyType' = BodyType.STATIC
    name: str = 'Unnamed'

    density: float = 0.3
    restitution: float = 0.8
    friction: float = 0.3

    linear_damping: float = 0
    angular_damping: float = 0
    fixed_rotation: bool = False

    friction_players: bool = False
    anti_tunnel: bool = False

    collide_mask: 'CollideFlag' = CollideFlag.ALL
    collide_group: 'CollideGroup' = CollideGroup.A
