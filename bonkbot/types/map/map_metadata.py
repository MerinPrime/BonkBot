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

    @staticmethod
    def from_json(data: dict) -> 'MapMetadata':
        metadata = MapMetadata()
        metadata.name = data.get('n', 'noname')
        metadata.author = data.get('a', 'noauthor')
        metadata.database_version = data.get('dbv', 2)
        metadata.database_id = data.get('dbid', -1)
        metadata.original_author = data.get('rxa', '')
        metadata.original_name = data.get('rxn', '')
        metadata.original_database_version = data.get('rxdb', 1)
        metadata.original_database_id = data.get('rxid', 0)
        metadata.is_published = data.get('pub', False)
        metadata.contributors = data.get('cr', [])
        metadata.date = data.get('date', '')
        metadata.auth_id = data.get('authid', -1)
        metadata.mode = Mode.from_mode_code(data.get('mo', ''))
        metadata.votes_down = data.get('vd')
        metadata.votes_up = data.get('vu')
        return metadata
