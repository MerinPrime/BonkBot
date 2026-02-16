from typing import TYPE_CHECKING, Tuple

from attrs import define, field

from .joint import Joint

if TYPE_CHECKING:
    from .....pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJoint.ts
# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJointProperties.ts
@define(slots=True, auto_attribs=True)
class DistanceJoint(Joint):
    softness: float = field(default=0.0)  # -99999,+99999
    damping: float = field(default=0.0)  # -99999,+99999
    pivot: Tuple[float, float] = field(default=(0, 0))  # -99999,+99999
    attach: Tuple[float, float] = field(default=(0, 0))  # -99999,+99999
    break_force: float = field(default=0.0)  # 0-99999999
    collide_connected: bool = field(default=False)
    draw_line: bool = field(default=True)
    body_a_id: int = field(default=-1)  # -1 or 0-32767
    body_b_id: int = field(default=-1)  # -1 or 0-32767

    def to_json(self) -> dict:
        return {
            'type': 'd',
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
