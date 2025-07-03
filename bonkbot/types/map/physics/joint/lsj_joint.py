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
class LSJJoint(Joint):
    position: Tuple[float, float] = field(default=(0, 0), converter=convert_to_float_vector,
                                          validator=validate_vector_range(-99999999, 99999999))
    spring_force: float = field(default=0.0, converter=float, validator=validate_float(-99999999, 99999999))
    spring_length: float = field(default=0.0, converter=float, validator=validate_float(-99999999, 99999999))
    break_force: float = field(default=0.0, converter=float, validator=validate_float(0, 99999999))
    collide_connected: bool = field(default=False, validator=validate_bool())
    draw_line: bool = field(default=True, validator=validate_bool())
    body_a_id: int = field(default=-1, validator=validate_int(-1, 32767))
    body_b_id: int = field(default=-1, validator=validate_int(-1, 32767))

    def to_json(self) -> dict:
        return {
            'sax': self.position[0],
            'say': self.position[1],
            'sf': self.spring_force,
            'slen': self.spring_length,
            'ba': self.body_a_id,
            'bb': self.body_b_id,
            'd': {
                'cc': self.collide_connected,
                'bf': self.break_force,
                'dl': self.draw_line,
            },
        }

    def from_json(self, data: dict) -> 'LSJJoint':
        self.body_a_id = data['ba']
        self.body_b_id = data['bb']
        self.position = (data['sax'], data['say'])
        self.spring_force = data['sf']
        self.spring_length = data['slen']
        self.collide_connected = data['d']['cc']
        self.break_force = data['d']['bf']
        self.draw_line = data['d']['dl']
        return self

    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_float64(self.position[0])
        buffer.write_float64(self.position[1])
        buffer.write_float64(self.spring_force)
        buffer.write_float64(self.spring_length)
        buffer.write_int16(self.body_a_id)
        buffer.write_int16(self.body_b_id)
        buffer.write_bool(self.collide_connected)
        buffer.write_float64(self.break_force)
        buffer.write_bool(self.draw_line)

    def from_buffer(self, buffer: 'ByteBuffer') -> 'LSJJoint':
        self.position = (buffer.read_float64(), buffer.read_float64())
        self.spring_force = buffer.read_float64()
        self.spring_length = buffer.read_float64()
        self.body_a_id = buffer.read_int16()
        self.body_b_id = buffer.read_int16()
        self.collide_connected = buffer.read_bool()
        self.break_force = buffer.read_float64()
        self.draw_line = buffer.read_bool()
        return self
