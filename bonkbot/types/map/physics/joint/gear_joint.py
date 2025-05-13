from dataclasses import dataclass

from .joint import Joint


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJoint.ts
# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJointProperties.ts
@dataclass
class GearJoint(Joint):
    name: str = 'Gear Joint'
    ratio: float = 1
    joint_a_id: int = -1
    joint_b_id: int = -1
