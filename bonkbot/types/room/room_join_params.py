from dataclasses import dataclass
from typing import Optional, Union


@dataclass(frozen=True)
class RoomJoinParams:
    room_id: int
    password: Optional[str] = None
    bypass: Optional[str] = None
    name: Union[str, None] = None
