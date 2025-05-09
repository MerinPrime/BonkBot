from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .body.body import Body
    from .fixture import Fixture
    from .joint.joint import Joint
    from .shape.shape import Shape


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IMapPhysics.ts
@dataclass
class MapPhysics:
    bodies: List['Body'] = field(default_factory=list)
    fixtures: List['Fixture'] = field(default_factory=list)
    joints: List['Joint'] = field(default_factory=list)
    shapes: List['Shape'] = field(default_factory=list)
    bro: List[int] = field(default_factory=list)
    ppm: int = 12
