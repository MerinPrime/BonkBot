from typing import TYPE_CHECKING, List, Optional

from attrs import define, field

from ...utils.validation import (
    validate_bool,
    validate_contributors,
    validate_int,
    validate_int_opts,
    validate_opt_int,
    validate_opt_str,
    validate_str,
    validate_type,
)
from ..mode import Mode

if TYPE_CHECKING:
    from ...pson import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IMapMetadata.ts
@define(slots=True, auto_attribs=True)
class MapMetadata:
    name: str = field(default='noname', validator=validate_str(25))
    author: str = field(default='noauthor', validator=validate_str(15))
    database_version: int = field(default=2, validator=validate_int_opts((1, 2)))
    database_id: int = field(default=-1, validator=validate_int())
    original_author: str = field(default='', validator=validate_str(15))
    original_name: str = field(default='', validator=validate_str(25))
    original_database_version: int = field(default=1, validator=validate_int_opts((1, 2)))
    original_database_id: int = field(default=0, validator=validate_int(0, 9999999999))
    is_published: bool = field(default=False, validator=validate_bool())
    contributors: List[str] = field(factory=list, validator=validate_contributors())
    date: str = field(default='', validator=validate_opt_str())
    auth_id: int = field(default=-1, validator=validate_int())
    mode: 'Mode' = field(default=Mode.NONE, validator=validate_type(Mode))
    votes_down: Optional[int] = field(default=None, validator=validate_opt_int(0))
    votes_up: Optional[int] = field(default=None, validator=validate_opt_int(0))

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
