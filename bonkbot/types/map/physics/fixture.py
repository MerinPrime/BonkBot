from typing import TYPE_CHECKING, Optional

from attrs import define, field

if TYPE_CHECKING:
    from ....pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IFixture.ts
@define(slots=True, auto_attribs=True)
class Fixture:
    shape_id: int = field(default=-1)

    name: str = field(default='Def Fix')
    color: int = field(default=0x4F7CAC)

    density: Optional[float] = field(default=0.3)  # 0-99999
    restitution: Optional[float] = field(default=0.8)  # -99999,+99999
    friction: Optional[float] = field(default=0.3)  # 0-99999

    friction_players: Optional[bool] = field(default=None)
    inner_grapple: Optional[bool] = field(default=None)

    no_grapple: bool = field(default=False)
    no_physics: bool = field(default=False)
    death: bool = field(default=False)

    sn: Optional[bool] = field(default=None)
    fs: Optional[str] = field(default=None)
    zp: Optional[int] = field(default=None)

    def to_json(self) -> dict:
        return {
            'd': self.death,
            'f': self.color,
            'fp': self.friction_players,
            'de': self.density,
            'fr': self.friction,
            're': self.restitution,
            'n': self.name,
            'ng': self.no_grapple,
            'np': self.no_physics,
            'sh': self.shape_id,
            'ig': self.inner_grapple,
            'sn': self.sn,
            'fs': self.fs,
            'zp': self.zp,
        }

    def from_json(self, data: dict) -> 'Fixture':
        self.death = data['d']
        self.color = data['f']
        self.friction_players = data['fp']
        self.density = data['de']
        self.friction = data['fr']
        self.restitution = data['re']
        self.name = data['n']
        self.no_grapple = data['ng']
        self.no_physics = data['np']
        self.shape_id = data['sh']
        self.inner_grapple = data.get('ig')
        self.sn = data.get('sn')
        self.fs = data.get('fs')
        self.zp = data.get('zp')
        return self

    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_int16(self.shape_id)
        buffer.write_utf(self.name)
        buffer.write_float64(
            self.friction if self.friction is not None else 1.7976931348623157e308,
        )
        buffer.write_int16((None, False, True).index(self.friction_players))
        buffer.write_float64(
            self.restitution
            if self.restitution is not None
            else 1.7976931348623157e308,
        )
        buffer.write_float64(
            self.density if self.density is not None else 1.7976931348623157e308,
        )
        buffer.write_uint32(self.color)
        buffer.write_bool(self.death)
        buffer.write_bool(self.no_physics)
        buffer.write_bool(self.no_grapple)
        buffer.write_bool(
            self.inner_grapple if self.inner_grapple is not None else False,
        )

    def from_buffer(self, buffer: 'ByteBuffer', version: int) -> 'Fixture':
        self.shape_id = buffer.read_int16()
        self.name = buffer.read_utf()

        friction = buffer.read_float64()
        if friction == 1.7976931348623157e308:
            friction = None
        self.friction = friction

        self.friction_players = (None, False, True)[buffer.read_int16()]

        restitution = buffer.read_float64()
        if restitution == 1.7976931348623157e308:
            restitution = None
        self.restitution = restitution

        density = buffer.read_float64()
        if density == 1.7976931348623157e308:
            density = None
        self.density = density

        self.color = buffer.read_uint32()
        self.death = buffer.read_bool()
        self.no_physics = buffer.read_bool()

        if version >= 11:
            self.no_grapple = buffer.read_bool()
        if version >= 12:
            self.inner_grapple = buffer.read_bool()
        return self
