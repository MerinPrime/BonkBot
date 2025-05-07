from dataclasses import dataclass
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..mode import Mode


@dataclass
class MapMetadata:
    author: str
    name: str
    database_version: int
    database_id: int
    original_author: str
    original_name: str
    original_database_version: int
    original_database_id: int
    public: bool
    contributors: List[str]
    date: str
    author_id: int
    mode: "Mode"
    votes_down: int
    votes_up: int
