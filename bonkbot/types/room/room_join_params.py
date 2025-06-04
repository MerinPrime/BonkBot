from typing import Optional, Union

import attrs

from bonkbot.types import Server


@attrs.define(slots=True, auto_attribs=True, frozen=True)
class RoomJoinParams:
    room_address: Union[str, int]
    name: Union[str, None]
    password: Optional[str]
    bypass: Optional[str]
    server: Server
