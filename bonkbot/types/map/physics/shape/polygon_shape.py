from typing import TYPE_CHECKING, List, Tuple

from attrs import define, field

from .....utils.validation import (
    convert_to_float_vector_list,
    validate_float,
    validate_vector_list_range,
)
from .shape import Shape

if TYPE_CHECKING:
    from .....pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IShape.ts
@define(slots=True, auto_attribs=True)
class PolygonShape(Shape):
    angle: float = field(default=0.0, converter=float, validator=validate_float(-999, 999))
    scale: float = field(default=1.0, converter=float, validator=validate_float(-999, 999))
    vertices: List[Tuple[float, float]] = field(factory=list, converter=convert_to_float_vector_list,
                                                validator=validate_vector_list_range(-99999, 99999))

    def to_json(self) -> dict:
        return {
            'type': 'po',
            'v': self.vertices,
            's': self.scale,
            'a': self.angle,
            'c': self.position,
        }

    def from_json(self, data: dict) -> 'PolygonShape':
        self.vertices = data['v']
        self.scale = data['s']
        self.angle = data['a']
        self.position = data['c']
        return self

    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_float64(self.scale)
        buffer.write_float64(self.angle)
        buffer.write_float64(self.position[0])
        buffer.write_float64(self.position[1])
        buffer.write_int16(len(self.vertices))
        for x, y in self.vertices:
            buffer.write_float64(x)
            buffer.write_float64(y)

    def from_buffer(self, buffer: 'ByteBuffer') -> 'PolygonShape':
        self.scale = buffer.read_float64()
        self.angle = buffer.read_float64()
        self.position = (buffer.read_float64(), buffer.read_float64())
        vertices = []
        for _ in range(buffer.read_int16()):
            vertices.append((buffer.read_float64(), buffer.read_float64()))
        self.vertices = vertices
        return self
