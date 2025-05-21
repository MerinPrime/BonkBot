from dataclasses import dataclass
from typing import Tuple

from .joint import Joint


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJoint.ts
# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJointProperties.ts
@dataclass
class LSJJoint(Joint):
    position: Tuple[float, float] = (0, 0)
    spring_force: float = 0
    spring_length: float = 0
    break_force: float = 0
    collide_connected: bool = False
    draw_line: bool = True
    shape_a_id: int = -1
    shape_b_id: int = -1
