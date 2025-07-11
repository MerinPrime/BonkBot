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
class RevoluteJoint(Joint):
    from_angle: float = field(default=0.0, converter=float, validator=validate_float(-999, 999))
    to_angle: float = field(default=0.0, converter=float, validator=validate_float(-999, 999))
    turn_force: float = field(default=0.0, converter=float, validator=validate_float(-99999999, 99999999))
    motor_speed: float = field(default=0.0, converter=float, validator=validate_float(-99999999, 99999999))
    enable_limit: bool = field(default=False, validator=validate_bool())
    enable_motor: bool = field(default=False, validator=validate_bool())
    pivot: Tuple[float, float] = field(default=(0, 0), converter=convert_to_float_vector,
                                       validator=validate_vector_range(-99999, 99999))
    break_force: float = field(default=0.0, converter=float, validator=validate_float(0, 99999999))
    collide_connected: bool = field(default=False, validator=validate_bool())
    draw_line: bool = field(default=True, validator=validate_bool())
    body_a_id: int = field(default=-1, validator=validate_int(-1, 32767))
    body_b_id: int = field(default=-1, validator=validate_int(-1, 32767))
    
    def to_json(self) -> dict:
        return {
            'type': 'rv',
            'aa': self.pivot,
            'ba': self.body_a_id,
            'bb': self.body_b_id,
            'd': {
                'la': self.from_angle,
                'ua': self.to_angle,
                'mmt': self.turn_force,
                'ms': self.motor_speed,
                'el': self.enable_limit,
                'em': self.enable_motor,
                'cc': self.collide_connected,
                'bf': self.break_force,
                'dl': self.draw_line,
            },
        }

    def from_json(self, data: dict) -> 'RevoluteJoint':
        self.from_angle = data['d']['la']
        self.to_angle = data['d']['ua']
        self.turn_force = data['d']['mmt']
        self.motor_speed = data['d']['ms']
        self.enable_limit = data['d']['el']
        self.enable_motor = data['d']['em']
        self.pivot = data['aa']
        self.body_a_id = data['ba']
        self.body_b_id = data['bb']
        self.collide_connected = data['d']['cc']
        self.break_force = data['d']['bf']
        self.draw_line = data['d']['dl']
        return self

    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_float64(self.from_angle)
        buffer.write_float64(self.to_angle)
        buffer.write_float64(self.turn_force)
        buffer.write_float64(self.motor_speed)
        buffer.write_bool(self.enable_limit)
        buffer.write_bool(self.enable_motor)
        buffer.write_float64(self.pivot[0])
        buffer.write_float64(self.pivot[1])
        buffer.write_int16(self.body_a_id)
        buffer.write_int16(self.body_b_id)
        buffer.write_bool(self.collide_connected)
        buffer.write_float64(self.break_force)
        buffer.write_bool(self.draw_line)

    def from_buffer(self, buffer: 'ByteBuffer') -> 'RevoluteJoint':
        self.from_angle = buffer.read_float64()
        self.to_angle = buffer.read_float64()
        self.turn_force = buffer.read_float64()
        self.motor_speed = buffer.read_float64()
        self.enable_limit = buffer.read_bool()
        self.enable_motor = buffer.read_bool()
        self.pivot = (buffer.read_float64(), buffer.read_float64())
        self.body_a_id = buffer.read_int16()
        self.body_b_id = buffer.read_int16()
        self.collide_connected = buffer.read_bool()
        self.break_force = buffer.read_float64()
        self.draw_line = buffer.read_bool()
        return self
