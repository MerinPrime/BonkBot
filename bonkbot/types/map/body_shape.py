from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .collide import CollideFlag, CollideGroup
    from .shape_body_type import ShapeBodyType


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IBodyShape.ts
@dataclass
class BodyShape:
    name: str
    body_type: 'ShapeBodyType'
    fric_players: bool
    collide_mask: 'CollideFlag'
    collide_group: 'CollideGroup'
    linear_damping: float
    angular_damping: float
    density: float
    friction: float
    restitution: float
    fixed_rotation: bool
    anti_tunnel: bool
