from dataclasses import dataclass
from typing import Tuple

from .joint import Joint


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJoint.ts
# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJointProperties.ts
@dataclass
class DistanceJoint(Joint):
    softness: float = 0
    damping: float = 0
    pivot: Tuple[float, float] = (0, 0)
    attach: Tuple[float, float] = (0, 0)
    break_force: float = 0
    collide_connected: bool = False
    draw_line: bool = True
    body_a_id: int = -1
    body_b_id: int = -1
