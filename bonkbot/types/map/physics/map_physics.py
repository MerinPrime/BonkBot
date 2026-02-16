from typing import List

from attrs import define, field

from ....utils.validation import validate_int, validate_int_list, validate_type_list
from .body.body import Body
from .fixture import Fixture
from .joint.joint import Joint
from .shape.shape import Shape


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IMapPhysics.ts
@define(slots=True, auto_attribs=True)
class MapPhysics:
    bodies: List['Body'] = field(
        factory=list,
        validator=validate_type_list(Body, 32767),
    )
    fixtures: List['Fixture'] = field(
        factory=list,
        validator=validate_type_list(Fixture, 32767),
    )
    joints: List['Joint'] = field(
        factory=list,
        validator=validate_type_list(Joint, 100),
    )
    shapes: List['Shape'] = field(
        factory=list,
        validator=validate_type_list(Shape, 32767),
    )
    bro: List[int] = field(
        factory=list,
        validator=validate_int_list(0, 32767, 0, 32767),
    )
    ppm: int = field(default=12, validator=validate_int(5, 30))
