from typing import Optional

import attrs

from bonkbot.types import Server


@attrs.define(slots=True, auto_attribs=True, frozen=True)
class RoomCreateParams:
    name: Optional[str]
    password: str
    unlisted: bool
    max_players: int
    min_level: int
    max_level: int
    server: 'Server'
