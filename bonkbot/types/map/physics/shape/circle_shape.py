from dataclasses import dataclass
from typing import Tuple

from .shape import Shape


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IShape.ts
@dataclass
class CircleShape(Shape):
    radius: float = 25
    position: Tuple[float, float] = (0, 0)
    shrink: bool = False
