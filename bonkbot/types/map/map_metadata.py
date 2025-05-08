from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ..mode import Mode


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IMapMetadata.ts
@dataclass
class MapMetadata:
    name: str
    author: str
    database_version: int
    database_id: int
    original_author: str
    original_name: str
    original_database_version: int
    original_database_id: int
    is_owner: bool
    contributors: List[str]
    date: str
    auth_id: int
    mode: 'Mode'
    votes_down: Optional[int]
    votes_up: Optional[int]
