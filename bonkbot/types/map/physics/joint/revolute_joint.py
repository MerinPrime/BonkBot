from dataclasses import dataclass
from typing import Tuple

from .joint import Joint


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJoint.ts
# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJointProperties.ts
@dataclass
class RevoluteJoint(Joint):
    from_angle: float = 0
    to_angle: float = 0
    turn_force: float = 0
    motor_speed: float = 0
    enable_limit: bool = False
    enable_motor: bool = False
    pivot: Tuple[float, float] = (0, 0)
    break_force: float = 0
    collide_connected: bool = False
    draw_line: bool = True
    body_a_id: int = -1
    body_b_id: int = -1
