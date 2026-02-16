from typing import Optional

from attrs import define


@define(slots=True, auto_attribs=True, frozen=True)
class Friend:
    name: str
    dbid: Optional[int]
    room_id: Optional[int]
