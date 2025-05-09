from dataclasses import dataclass
from typing import Optional


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IFixture.ts
@dataclass
class Fixture:
    shape_id: int

    name: str = 'Def Fix'
    color: float = 0x4F7CAC

    density: float = 0.3
    restitution: float = 0.8
    friction: Optional[float] = 0.3

    friction_players: Optional[bool] = None
    inner_grapple: Optional[bool] = None

    no_grapple: bool = False
    no_physics: bool = False
    death: bool = False

    sn: Optional[bool] = None
    fs: Optional[bool] = None
    zp: Optional[int] = None
