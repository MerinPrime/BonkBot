from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class RoomCreateParams:
    name: Union[str, None] = None
    password: str = ''
    unlisted: bool = False
    max_players: int = 6
    min_level: int = 0
    max_level: int = 999
