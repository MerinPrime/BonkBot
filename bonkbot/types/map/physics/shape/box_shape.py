from dataclasses import dataclass
from typing import Tuple

from .shape import Shape


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IShape.ts
@dataclass
class BoxShape(Shape):
    width: float = 10
    height: float = 40
    angle: float = 0.0
    shrink: bool = False
