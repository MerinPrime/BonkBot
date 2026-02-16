from typing import List

from attrs import define, field

from .body.body import Body
from .fixture import Fixture
from .joint.joint import Joint
from .shape.shape import Shape


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IMapPhysics.ts
@define(slots=True, auto_attribs=True)
class MapPhysics:
    bodies: List['Body'] = field(factory=list)  # 32767
    fixtures: List['Fixture'] = field(factory=list)  # 32767
    joints: List['Joint'] = field(factory=list)  # 100
    shapes: List['Shape'] = field(factory=list)  # 32767
    bro: List[int] = field(factory=list)  # 32767
    ppm: int = field(default=12)  # 5-30
