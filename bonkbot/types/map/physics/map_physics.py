from dataclasses import dataclass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .body.body import Body
    from .fixture import Fixture
    from .joint.joint import Joint
    from .shape.shape import Shape


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IMapPhysics.ts
@dataclass
class MapPhysics:
    bodies: List['Body']
    fixtures: List['Fixture']
    joints: List['Joint']
    shapes: List['Shape']
    bro: List[int]
    ppm: float
