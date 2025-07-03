from typing import TYPE_CHECKING

from attrs import define, field

from .....utils.validation import validate_bool, validate_float
from .shape import Shape

if TYPE_CHECKING:
    from .....pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IShape.ts
@define(slots=True, auto_attribs=True)
class CircleShape(Shape):
    radius: float = field(default=25.0, converter=float, validator=validate_float(0, 99999))
    shrink: bool = field(default=False, validator=validate_bool())

    def to_json(self) -> dict:
        return {
            'type': 'ci',
            'r': self.radius,
            'c': self.position,
            'sk': self.shrink,
        }

    def from_json(self, data: dict) -> 'CircleShape':
        self.radius = data['r']
        self.position = data['c']
        self.shrink = data['sk']
        return self

    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_float64(self.radius)
        buffer.write_float64(self.position[0])
        buffer.write_float64(self.position[1])
        buffer.write_bool(self.shrink)

    def from_buffer(self, buffer: 'ByteBuffer') -> 'CircleShape':
        self.radius = buffer.read_float64()
        self.position = (buffer.read_float64(), buffer.read_float64())
        self.shrink = buffer.read_bool()
        return self
