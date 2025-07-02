import enum
from typing import TYPE_CHECKING, Tuple

from attrs import define, field

from bonkbot.utils.validation import (
    validate_bool,
    validate_float,
    validate_type,
    validate_vector_range,
)

if TYPE_CHECKING:
    from .....pson.bytebuffer import ByteBuffer


class ForceZoneType(enum.IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    CENTER_PUSH = 2
    CENTER_PULL = 3

    @staticmethod
    def from_id(type_id: int) -> 'ForceZoneType':
        for force_zone_type in ForceZoneType:
            if type_id == force_zone_type.value:
                return force_zone_type

# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IBodyForceZoneProperties.ts
@define(slots=True, auto_attribs=True)
class ForceZone:
    enabled: bool = field(default=False, validator=validate_bool())
    type: 'ForceZoneType' = field(default=ForceZoneType.ABSOLUTE, validator=validate_type(ForceZoneType))
    force: Tuple[float, float] = field(default=(0, 0), validator=validate_vector_range(-999999, 999999))
    '''FOR ABSOLUTE & RELATIVE'''
    center_force: float = field(default=0, converter=float, validator=validate_float(0, 999999))
    '''FOR CENTER_PUSH & CENTER_PULL'''
    push_players: bool = field(default=True, validator=validate_bool())
    push_bodies: bool = field(default=True, validator=validate_bool())
    push_arrows: bool = field(default=True, validator=validate_bool())
    
    def to_json(self) -> dict:
        return {
            'on': self.enabled,
            'x': self.force[0],
            'y': self.force[1],
            't': self.type.value,
            'd': self.push_players,
            'p': self.push_bodies,
            'a': self.push_arrows,
            'cf': self.center_force,
        }

    def from_json(self, data: dict) -> 'ForceZone':
        self.enabled = data['on']
        self.force = (data['x'], data['y'])
        self.type = ForceZoneType.from_id(data['t'])
        self.push_players = data['d']
        self.push_bodies = data['p']
        self.push_arrows = data['a']
        self.center_force = data['cf']
        return self

    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_bool(self.enabled)
        if self.enabled:
            buffer.write_float64(self.force[0])
            buffer.write_float64(self.force[1])
            buffer.write_bool(self.push_players)
            buffer.write_bool(self.push_bodies)
            buffer.write_bool(self.push_arrows)
            buffer.write_int16(self.type.value)
            buffer.write_float64(self.center_force)

    def from_buffer(self, buffer: 'ByteBuffer', version: int) -> 'ForceZone':
        self.enabled = buffer.read_bool()
        if self.enabled:
            self.force = (buffer.read_float64(), buffer.read_float64())
            self.push_players = buffer.read_bool()
            self.push_bodies = buffer.read_bool()
            self.push_arrows = buffer.read_bool()
            if version >= 15:
                self.type = ForceZoneType.from_id(buffer.read_int16())
                self.center_force = buffer.read_float64()
        return self
