from typing import TYPE_CHECKING, Optional

from attrs import define, field

from ...utils.validation import validate_bool, validate_float, validate_int

if TYPE_CHECKING:
    from ...pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/avatar/Layer.ts
# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/avatar/Avatar.ts
@define(slots=True, auto_attribs=True)
class Layer:
    id: int = field(default=1, validator=validate_int(1, 115))
    scale: float = field(
        default=0.25,
        converter=float,
        validator=validate_float(-10, 10),
    )
    angle: float = field(
        default=0,
        converter=float,
        validator=validate_float(-9999, 9999),
    )
    x: float = field(
        default=0,
        converter=float,
        validator=validate_float(-99999, 99999),
    )
    y: float = field(
        default=0,
        converter=float,
        validator=validate_float(-99999, 99999),
    )
    flip_x: bool = field(default=False, validator=validate_bool())
    flip_y: bool = field(default=False, validator=validate_bool())
    color: int = field(default=0, validator=validate_int(0, 16777215))

    @staticmethod
    def from_buffer(buffer: 'ByteBuffer') -> Optional['Layer']:
        if buffer.read_uint8() != 10:
            return None
        if buffer.read_uint8() == 7:
            buffer.read_uint8()
            buffer.read_uint8()
            buffer.read_uint8()
        buffer.read_int16()
        layer = Layer(
            id=buffer.read_uint16(),
            scale=buffer.read_float32(),
            angle=buffer.read_float32(),
            x=buffer.read_float32(),
            y=buffer.read_float32(),
            flip_x=buffer.read_bool(),
            flip_y=buffer.read_bool(),
            color=buffer.read_int32(),
        )
        return layer

    @staticmethod
    def from_json(data: dict) -> 'Layer':
        layer = Layer(
            id=data['id'],
            scale=data['scale'],
            angle=data['angle'],
            x=data['x'],
            y=data['y'],
            flip_x=data['flipX'],
            flip_y=data['flipY'],
            color=data['color'],
        )
        return layer

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'scale': self.scale,
            'angle': self.angle,
            'x': self.x,
            'y': self.y,
            'flipX': self.flip_x,
            'flipY': self.flip_y,
            'color': self.color,
        }
