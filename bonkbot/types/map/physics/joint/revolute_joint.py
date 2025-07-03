from typing import TYPE_CHECKING, Tuple

from attrs import define

from .joint import Joint

if TYPE_CHECKING:
    from .....pson.bytebuffer import ByteBuffer

# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJoint.ts
# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJointProperties.ts
@define(slots=True, auto_attribs=True)
class RevoluteJoint(Joint):
    from_angle: float = 0
    to_angle: float = 0
    turn_force: float = 0
    motor_speed: float = 0
    enable_limit: bool = False
    enable_motor: bool = False
    pivot: Tuple[float, float] = (0, 0)
    break_force: float = 0
    collide_connected: bool = False
    draw_line: bool = True
    body_a_id: int = -1
    body_b_id: int = -1
    
    def to_json(self) -> dict:
        return {
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
