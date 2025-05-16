from dataclasses import dataclass, field
from typing import List, Optional

from ..mode import Mode


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IMapMetadata.ts
@dataclass
class MapMetadata:
    name: str = 'noname'
    author: str = 'noauthor'
    database_version: int = 2
    database_id: int = -1
    original_author: str = ''
    original_name: str = ''
    original_database_version: int = 1
    original_database_id: int = 0
    is_published: bool = False
    contributors: List[str] = field(default_factory=list)
    date: str = ''
    auth_id: int = -1
    mode: 'Mode' = Mode.NONE
    votes_down: Optional[int] = None
    votes_up: Optional[int] = None
