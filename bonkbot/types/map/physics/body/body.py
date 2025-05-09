from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .body_force import BodyForce
from .body_shape import BodyShape
from .force_zone import ForceZone


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IBody.ts
@dataclass
class Body:
    name: Optional[str] = None

    position: Tuple[float, float] = (0, 0)
    linear_velocity: Tuple[float, float] = (0, 0)
    angle: float = 0
    angular_velocity: float = 0

    fixtures: List[int] = field(default_factory=list)
    shape: 'BodyShape' = field(default_factory=BodyShape)
    force: 'BodyForce' = field(default_factory=BodyForce)
    force_zone: 'ForceZone' = field(default_factory=ForceZone)
