from typing import TYPE_CHECKING

from attrs import define

if TYPE_CHECKING:
    from ..mode import Mode


@define(slots=True, auto_attribs=True, frozen=True)
class RoomInfo:
    name: str
    id: int
    players: int
    max_players: int
    has_password: bool
    mode: 'Mode'
    min_level: int
    max_level: int
