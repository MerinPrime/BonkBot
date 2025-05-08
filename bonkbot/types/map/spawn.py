from dataclasses import dataclass
from typing import Optional, Tuple


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/ISpawn.ts
@dataclass
class Spawn:
    name: str
    allowed_ffa: bool
    blue: bool
    red: bool
    green: Optional[bool]
    yellow: Optional[bool]
    priority: float
    position: Tuple[float, float]
    velocity: Tuple[float, float]
