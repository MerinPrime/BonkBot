from dataclasses import dataclass
from typing import Optional


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJointProperties.ts
@dataclass
class JointProperties:
    enable_motor: Optional[bool]
    enable_limit: Optional[bool]
    break_force: Optional[float]
    from_angle: Optional[float]
    to_angle: Optional[float]
    turn_force: Optional[float]
    motor_speed: Optional[float]

    damping: Optional[float]
    softness: Optional[float]

    col_attached: bool
    draw_line: Optional[bool]

    lower_translation: Optional[float]
    upper_translation: Optional[float]
    max_motor_force: Optional[float]
    change_side: Optional[bool]
