from typing import TYPE_CHECKING

from attrs import define, field

from .....utils.validation import validate_float, validate_int, validate_str
from .joint import Joint

if TYPE_CHECKING:
    from .....pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJoint.ts
# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJointProperties.ts
@define(slots=True, auto_attribs=True)
class GearJoint(Joint):
    name: str = field(default='Gear Joint', validator=validate_str(29))
    ratio: float = field(default=0.0, converter=float, validator=validate_float(-99999999, 99999999))
    joint_a_id: int = field(default=0, validator=validate_int(0, 100))
    joint_b_id: int = field(default=0, validator=validate_int(0, 100))

    def to_json(self) -> dict:
        return {
            'type': 'g',
            'n': self.name,
            'ja': self.joint_a_id,
            'jb': self.joint_b_id,
            'r': self.ratio,
        }

    def from_json(self, data: dict) -> 'GearJoint':
        self.name = data['n']
        self.joint_a_id = data['ja']
        self.joint_b_id = data['jb']
        self.ratio = data['r']
        return self

    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_utf(self.name)
        buffer.write_float64(self.ratio)
        buffer.write_int16(self.joint_a_id)
        buffer.write_int16(self.joint_b_id)

    def from_buffer(self, buffer: 'ByteBuffer') -> 'GearJoint':
        self.name = buffer.read_utf()
        self.ratio = buffer.read_float64()
        self.joint_a_id = buffer.read_int16()
        self.joint_b_id = buffer.read_int16()
        return self
