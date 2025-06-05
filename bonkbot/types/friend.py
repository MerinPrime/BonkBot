from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Friend:
    name: str = ''
    dbid: Optional[int] = None
    room_id: Optional[int] = None
