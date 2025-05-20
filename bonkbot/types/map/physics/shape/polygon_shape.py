from dataclasses import dataclass, field
from typing import List, Tuple

from .shape import Shape


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IShape.ts
@dataclass
class PolygonShape(Shape):
    angle: float = 0
    scale: float = 1
    vertices: List[Tuple[float, float]] = field(default_factory=list)
