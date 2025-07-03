from typing import TYPE_CHECKING

from attrs import define, field

from .....utils.validation import validate_bool, validate_float
from .shape import Shape

if TYPE_CHECKING:
    from .....pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IShape.ts
@define(slots=True, auto_attribs=True)
class BoxShape(Shape):
    width: float = field(default=10.0, converter=float, validator=validate_float(0, 99999))
    height: float = field(default=40.0, converter=float, validator=validate_float(0, 99999))
    angle: float = field(default=0.0, converter=float, validator=validate_float(-999, 999))
    shrink: bool = field(default=False, validator=validate_bool())

    def to_json(self) -> dict:
        return {
            'type': 'bx',
            'w': self.width,
            'h': self.height,
            'c': self.position,
            'a': self.angle,
            'sk': self.shrink,
        }

    def from_json(self, data: dict) -> 'BoxShape':
        self.width = data['w']
        self.height = data['h']
        self.position = data['c']
        self.angle = data['a']
        self.shrink = data['sk']
        return self

    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_float64(self.width)
        buffer.write_float64(self.height)
        buffer.write_float64(self.position[0])
        buffer.write_float64(self.position[1])
        buffer.write_float64(self.angle)
        buffer.write_bool(self.shrink)

    def from_buffer(self, buffer: 'ByteBuffer') -> 'BoxShape':
        self.width = buffer.read_float64()
        self.height = buffer.read_float64()
        self.position = (buffer.read_float64(), buffer.read_float64())
        self.angle = buffer.read_float64()
        self.shrink = buffer.read_bool()
        return self
