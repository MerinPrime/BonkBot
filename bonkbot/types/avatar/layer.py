from typing import Dict, Union

import attrs

from ...pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/avatar/Layer.ts
# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/avatar/Avatar.ts
@attrs.define(slots=True, auto_attribs=True)
class Layer:
    id: int = attrs.field(default=1, validator=attrs.validators.and_(
        # Must be int in range [1, 115]
        attrs.validators.instance_of(int),
        attrs.validators.le(115),
        attrs.validators.ge(1),
    ))
    scale: float = attrs.field(default=0.25, validator=attrs.validators.and_(
        # Must be float in range [-10, 10]
        attrs.validators.instance_of(float),
        attrs.validators.le(10),
        attrs.validators.ge(-10),
    ))
    angle: float = attrs.field(default=0, validator=attrs.validators.and_(
        # Must be float in range [-9999, 9999]
        attrs.validators.instance_of(float),
        attrs.validators.le(9999),
        attrs.validators.ge(-9999),
    ))
    x: float = attrs.field(default=0, validator=attrs.validators.and_(
        # Must be float in range [-99999, 99999]
        attrs.validators.instance_of(float),
        attrs.validators.le(99999),
        attrs.validators.ge(-99999),
    ))
    y: float = attrs.field(default=0, validator=attrs.validators.and_(
        # Must be float in range [-99999, 99999]
        attrs.validators.instance_of(float),
        attrs.validators.le(99999),
        attrs.validators.ge(-99999),
    ))
    flip_x: bool = attrs.field(default=False, validator=attrs.validators.instance_of(bool))
    flip_y: bool = attrs.field(default=False, validator=attrs.validators.instance_of(bool))
    color: int = attrs.field(default=0, validator=attrs.validators.and_(
        # Must be int in range [0, 16777215]
        attrs.validators.instance_of(int),
        attrs.validators.le(0xFFFFFF),
        attrs.validators.ge(0x000000),
    ))

    @staticmethod
    def from_buffer(buffer: ByteBuffer) -> Union['Layer', None]:
        if buffer.read_uint8() != 10:
            return None
        if buffer.read_uint8() == 7:
            buffer.read_uint8()
            buffer.read_uint8()
            buffer.read_uint8()
        buffer.read_int16()
        layer = Layer(
            id = buffer.read_uint16(),
            scale = buffer.read_float32(),
            angle = buffer.read_float32(),
            x = buffer.read_float32(),
            y = buffer.read_float32(),
            flip_x = buffer.read_bool(),
            flip_y = buffer.read_bool(),
            color = buffer.read_int32(),
        )
        return layer

    @staticmethod
    def from_json(data: Dict) -> 'Layer':
        layer = Layer(
            id = data['id'],
            scale = data['scale'],
            angle = data['angle'],
            x = data['x'],
            y = data['y'],
            flip_x = data['flipX'],
            flip_y = data['flipY'],
            color = data['color'],
        )
        return layer

    def to_json(self) -> Dict:
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
