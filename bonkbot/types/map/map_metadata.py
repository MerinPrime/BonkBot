from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

from ..mode import Mode

if TYPE_CHECKING:
    from ...pson import ByteBuffer


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

    def to_json(self) -> dict:
        data = {
            'a': self.author,
            'n': self.name,
            'dbv': self.database_version,
            'dbid': self.database_id,
            'rxa': self.original_author,
            'rxn': self.original_name,
            'rxdb': self.original_database_version,
            'rxid': self.original_database_id,
            'pub': self.is_published,
            'cr': self.contributors,
            'date': self.date,
            'authid': self.auth_id,
            'mo': self.mode.mode,
        }
        if self.votes_down is not None:
            data['vd'] = self.votes_down
        if self.votes_up is not None:
            data['vu'] = self.votes_up
        return data
    
    def from_json(self, data: dict) -> 'MapMetadata':
        self.name = data['n']
        self.author = data['a']
        self.database_version = data['dbv']
        self.database_id = data['dbid']
        self.original_author = data['rxa']
        self.original_name = data['rxn']
        self.original_database_version = data['rxdb']
        self.original_database_id = data['rxid']
        self.is_published = data['pub']
        self.contributors = data['cr']
        self.date = data['date']
        self.auth_id = data['authid']
        self.mode = Mode.from_mode_code(data['mo'])
        self.votes_down = data.get('vd')
        self.votes_up = data.get('vu')
        return self

    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_utf(self.original_name)
        buffer.write_utf(self.original_author)
        buffer.write_int16(self.original_database_id)
        buffer.write_uint32(self.original_database_version)
        buffer.write_utf(self.name)
        buffer.write_utf(self.author)
        buffer.write_uint32(self.votes_up)
        buffer.write_uint32(self.votes_down)
        buffer.write_int16(len(self.contributors))
        for contributor in self.contributors:
            buffer.write_utf(contributor)
        buffer.write_utf(self.mode.mode)
        buffer.write_int32(self.database_id)
        buffer.write_bool(self.is_published)
        buffer.write_int32(self.database_version)

    def from_buffer(self, buffer: 'ByteBuffer', version: int) -> 'MapMetadata':
        self.original_name = buffer.read_utf()
        self.original_author = buffer.read_utf()
        self.original_database_id = buffer.read_uint32()
        self.original_database_version = buffer.read_int16()
        self.name = buffer.read_utf()
        self.author = buffer.read_utf()
        if version >= 10:
            self.votes_up = buffer.read_uint32()
            self.votes_down = buffer.read_uint32()
        if version >= 4:
            self.contributors = []
            contributors_count = buffer.read_int16()
            for _ in range(contributors_count):
                self.contributors.append(buffer.read_utf())
        if version >= 5:
            self.mode = Mode.from_mode_code(buffer.read_utf())
            self.database_id = buffer.read_int32()
        if version >= 7:
            self.is_published = buffer.read_bool()
        if version >= 8:
            self.database_version = buffer.read_int32()
        return self
