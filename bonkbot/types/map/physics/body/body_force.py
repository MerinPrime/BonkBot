from dataclasses import dataclass


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IBodyForce.ts
@dataclass
class BodyForce:
    force_x: float = 0
    force_y: float = 0
    is_relative: bool = False
    torque: float = 0
