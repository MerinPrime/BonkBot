from dataclasses import dataclass
from typing import Tuple


@dataclass
class Shape:
    position: Tuple[float, float] = (0, 0)
