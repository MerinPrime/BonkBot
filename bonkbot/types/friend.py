from dataclasses import dataclass
from typing import List, Union

from bonkbot.types.avatar.layer import Layer


@dataclass(frozen=True)
class Friend:
    name: str = ''
    dbid: Union[int, None] = None
    room_id: Union[int, None] = None
