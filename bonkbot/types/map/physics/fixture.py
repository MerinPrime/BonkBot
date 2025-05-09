from dataclasses import dataclass
from typing import Optional


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IFixture.ts
@dataclass
class Fixture:
    name: str
    color: float
    density: float
    fric_players: Optional[bool]
    friction: float
    death: bool
    inner_grapple: Optional[bool]
    no_grapple: bool
    no_physics: bool
    restitution: float
    shape_id: int
    sn: Optional[bool]
    fs: Optional[bool]
    zp: Optional[int]
