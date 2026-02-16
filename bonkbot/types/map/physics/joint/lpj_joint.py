from typing import TYPE_CHECKING, Tuple

from attrs import define, field

from .....utils.validation import (
    convert_to_float_vector,
    validate_bool,
    validate_float,
    validate_int,
    validate_vector_range,
)
from .joint import Joint

if TYPE_CHECKING:
    from .....pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJoint.ts
# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJointProperties.ts
@define(slots=True, auto_attribs=True)
class LPJJoint(Joint):
    position: Tuple[float, float] = field(
        default=(0, 0),
        converter=convert_to_float_vector,
        validator=validate_vector_range(-99999999, 99999999),
    )
    angle: float = field(
        default=0.0,
        converter=float,
        validator=validate_float(-99999999, 99999999),
    )
    force: float = field(
        default=0.0,
        converter=float,
        validator=validate_float(-99999999, 99999999),
    )
    pl: float = field(default=0.0)
    pu: float = field(default=0.0)
    path_length: float = field(
        default=0.0,
        converter=float,
        validator=validate_float(-99999999, 99999999),
    )
    path_speed: float = field(
        default=0.0,
        converter=float,
        validator=validate_float(-99999999, 99999999),
    )
    break_force: float = field(
        default=0.0,
        converter=float,
        validator=validate_float(0, 99999999),
    )
    collide_connected: bool = field(default=False, validator=validate_bool())
    draw_line: bool = field(default=True, validator=validate_bool())
    body_a_id: int = field(default=-1, validator=validate_int(-1, 32767))
    body_b_id: int = field(default=-1, validator=validate_int(-1, 32767))

    def to_json(self) -> dict:
        return {
            'type': 'lpj',
            'pax': self.position[0],
            'pay': self.position[1],
            'pa': self.angle,
            'pf': self.force,
            'pl': self.pl,
            'pu': self.pu,
            'plen': self.path_length,
            'pms': self.path_speed,
            'ba': self.body_a_id,
            'bb': self.body_b_id,
            'd': {
                'cc': self.collide_connected,
                'bf': self.break_force,
                'dl': self.draw_line,
            },
        }

    def from_json(self, data: dict) -> 'LPJJoint':
        self.position = (data['pax'], data['pay'])
        self.angle = data['pa']
        self.force = data['pf']
        self.pl = data['pl']
        self.pu = data['pu']
        self.path_length = data['plen']
        self.path_speed = data['pms']
        self.body_a_id = data['ba']
        self.body_b_id = data['bb']
        self.collide_connected = data['d']['cc']
        self.break_force = data['d']['bf']
        self.draw_line = data['d']['dl']
        return self

    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_float64(self.position[0])
        buffer.write_float64(self.position[1])
        buffer.write_float64(self.angle)
        buffer.write_float64(self.force)
        buffer.write_float64(self.pl)
        buffer.write_float64(self.pu)
        buffer.write_float64(self.path_length)
        buffer.write_float64(self.path_speed)
        buffer.write_int16(self.body_a_id)
        buffer.write_int16(self.body_b_id)
        buffer.write_bool(self.collide_connected)
        buffer.write_float64(self.break_force)
        buffer.write_bool(self.draw_line)

    def from_buffer(self, buffer: 'ByteBuffer') -> 'LPJJoint':
        self.position = (buffer.read_float64(), buffer.read_float64())
        self.angle = buffer.read_float64()
        self.force = buffer.read_float64()
        self.pl = buffer.read_float64()
        self.pu = buffer.read_float64()
        self.path_length = buffer.read_float64()
        self.path_speed = buffer.read_float64()
        self.body_a_id = buffer.read_int16()
        self.body_b_id = buffer.read_int16()
        self.collide_connected = buffer.read_bool()
        self.break_force = buffer.read_float64()
        self.draw_line = buffer.read_bool()
        return self
