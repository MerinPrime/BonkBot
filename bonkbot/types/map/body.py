from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from .body_force import BodyForce
    from .body_shape import BodyShape
    from .force_zone_properties import ForceZoneProperties


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IBody.ts
@dataclass
class Body:
    name: Optional[str]
    angle: float
    angle_velocity: float
    fx: List[int]
    position: Tuple[float, float]
    linear_velocity: Tuple[float, float]
    shape: 'BodyShape'
    force: Optional['BodyForce']
    force_zone: Optional['ForceZoneProperties']
