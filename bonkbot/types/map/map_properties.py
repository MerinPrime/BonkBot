from typing import TYPE_CHECKING, Optional

from attrs import define, field

if TYPE_CHECKING:
    from ...pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IMapProperties.ts
@define(slots=True, auto_attribs=True)
class MapProperties:
    grid_size: float = field(default=25)  # 2-100
    players_dont_collide: bool = field(default=False)
    respawn_on_death: bool = field(default=False)
    players_can_fly: bool = field(default=False)
    complex_physics: bool = field(default=False)
    a1: Optional[bool] = field(default=None)
    a2: Optional[bool] = field(default=None)
    a3: Optional[bool] = field(default=None)

    def to_json(self) -> dict:
        data = {
            'gd': self.grid_size,
            'nc': self.players_dont_collide,
            're': self.respawn_on_death,
            'fl': self.players_can_fly,
            'pq': 2 if self.complex_physics else 1,
        }
        if self.a1 is not None:
            data['a1'] = self.a1
        if self.a2 is not None:
            data['a2'] = self.a2
        if self.a3 is not None:
            data['a3'] = self.a3
        return data

    def from_json(self, data: dict) -> 'MapProperties':
        self.grid_size = data['gd']
        self.players_dont_collide = data['nc']
        self.respawn_on_death = data['re']
        self.players_can_fly = data['fl']
        self.complex_physics = data['pq'] == 2
        self.a1 = data.get('a1')
        self.a2 = data.get('a2')
        self.a3 = data.get('a3')
        return self

    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_bool(self.players_dont_collide)
        buffer.write_bool(self.respawn_on_death)
        buffer.write_int16(2 if self.complex_physics else 1)
        buffer.write_float32(self.grid_size)
        buffer.write_bool(self.players_can_fly)

    def from_buffer(self, buffer: 'ByteBuffer', version: int) -> 'MapProperties':
        self.respawn_on_death = buffer.read_bool()
        self.players_dont_collide = buffer.read_bool()
        if version >= 3:
            self.complex_physics = buffer.read_int16() == 2
        if 4 <= version <= 12:
            self.grid_size = buffer.read_int16()
        elif version >= 13:
            self.grid_size = buffer.read_float32()
        if version >= 9:
            self.players_can_fly = buffer.read_bool()

        return self
