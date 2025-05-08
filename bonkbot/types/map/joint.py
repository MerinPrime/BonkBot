from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from .joint_properties import JointProperties
    from .joint_type import JointType


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJoint.ts
@dataclass
class Joint:
    type: 'JointType'
    name: Optional[str]
    body_a_id: Optional[int]
    body_b_id: Optional[int]
    pivot: Optional[Tuple[float, float]]
    attach: Optional[Tuple[float, float]]
    properties: Optional['JointProperties']
    path_angle: Optional[float]
    start_x: Optional[float]
    start_y: Optional[float]
    path_force: Optional[float]
    path_length: Optional[float]
    path_speed: Optional[float]
    spring_force: Optional[float]
    spring_length: Optional[float]
    joint_a_id: Optional[int]
    joint_b_id: Optional[int]
    gear_ratio: Optional[float]
    axis: Optional[Tuple[float, float]]
    pu: Optional[float]
    pl: Optional[float]
