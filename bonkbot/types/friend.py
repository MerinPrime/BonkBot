from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Friend:
    name: str = ''
    dbid: Union[int, None] = None
    room_id: Union[int, None] = None
