from typing import Optional, Union

from attr import define

from ..server import Server


@define(slots=True, auto_attribs=True, frozen=True)
class RoomJoinParams:
    room_address: Union[str, int]
    name: Optional[str]
    password: Optional[str]
    bypass: Optional[str]
    server: Server
