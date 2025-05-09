from dataclasses import dataclass
from typing import Optional, Tuple


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/ISpawn.ts
@dataclass
class Spawn:
    name: str = 'Spawn'
    ffa: bool = True
    blue: bool = True
    red: bool = True
    green: Optional[bool] = None
    yellow: Optional[bool] = None
    priority: float = 5
    position: Tuple[float, float] = (400, 300)
    velocity: Tuple[float, float] = (0, 0)
