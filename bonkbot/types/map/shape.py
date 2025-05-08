from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from .shape_type import ShapeType


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IShape.ts
@dataclass
class Shape:
    type: 'ShapeType'
    angle: Optional[float]
    height: Optional[float]
    width: Optional[float]
    shrink: Optional[bool]
    radius: Optional[float]
    vertices: Optional[List[Tuple[float, float]]]
    scale: Optional[float]
    position: Tuple[float, float]
    l: Optional[bool]
