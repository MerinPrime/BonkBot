from dataclasses import dataclass

from .shape import Shape


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IShape.ts
@dataclass
class CircleShape(Shape):
    radius: float = 25
    shrink: bool = False
