from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..mode import Mode


@dataclass(frozen=True)
class RoomInfo:
    name: str
    id: int
    players: int
    max_players: int
    has_password: bool
    mode: 'Mode'
    min_level: int
    max_level: int
