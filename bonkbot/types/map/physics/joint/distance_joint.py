from typing import TYPE_CHECKING, Tuple

from attrs import define

from .joint import Joint

if TYPE_CHECKING:
    from .....pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJoint.ts
# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJointProperties.ts
@define(slots=True, auto_attribs=True)
class DistanceJoint(Joint):
    softness: float = 0
    damping: float = 0
    pivot: Tuple[float, float] = (0, 0)
    attach: Tuple[float, float] = (0, 0)
    break_force: float = 0
    collide_connected: bool = False
    draw_line: bool = True
    body_a_id: int = -1
    body_b_id: int = -1
    
    def to_json(self) -> dict:
        return {
            'aa': self.pivot,
            'ab': self.attach,
            'ba': self.body_a_id,
            'bb': self.body_b_id,
            'd': {
                'fh': self.softness,
                'dr': self.damping,
                'cc': self.collide_connected,
                'bf': self.break_force,
                'dl': self.draw_line,
            },
        }

    def from_json(self, data: dict) -> 'DistanceJoint':
        self.softness = data['d']['fh']
        self.damping = data['d']['dr']
        self.pivot = data['aa']
        self.attach = data['ab']
        self.body_a_id = data['ba']
        self.body_b_id = data['bb']
        self.collide_connected = data['d']['cc']
        self.break_force = data['d']['bf']
        self.draw_line = data['d']['dl']
        return self

    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_float64(self.softness)
        buffer.write_float64(self.damping)
        buffer.write_float64(self.pivot[0])
        buffer.write_float64(self.pivot[1])
        buffer.write_float64(self.attach[0])
        buffer.write_float64(self.attach[1])
        buffer.write_int16(self.body_a_id)
        buffer.write_int16(self.body_b_id)
        buffer.write_bool(self.collide_connected)
        buffer.write_float64(self.break_force)
        buffer.write_bool(self.draw_line)

    def from_buffer(self, buffer: 'ByteBuffer') -> 'DistanceJoint':
        self.softness = buffer.read_float64()
        self.damping = buffer.read_float64()
        self.pivot = (buffer.read_float64(), buffer.read_float64())
        self.attach = (buffer.read_float64(), buffer.read_float64())
        self.body_a_id = buffer.read_int16()
        self.body_b_id = buffer.read_int16()
        self.collide_connected = buffer.read_bool()
        self.break_force = buffer.read_float64()
        self.draw_line = buffer.read_bool()
        return self
