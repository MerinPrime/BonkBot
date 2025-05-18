from dataclasses import dataclass
from typing import Optional, Union

from bonkbot.types import Server


@dataclass(frozen=True)
class RoomJoinParams:
    room_address: Union[str, int]
    password: Optional[str] = None
    bypass: Optional[str] = None
    name: Union[str, None] = None
    server: Server = Server.WARSAW
