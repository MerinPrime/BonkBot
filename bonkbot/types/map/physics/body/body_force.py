from dataclasses import dataclass


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IBodyForce.ts
@dataclass
class BodyForce:
    force_x: float
    force_y: float
    is_relative: bool
    torque: float
