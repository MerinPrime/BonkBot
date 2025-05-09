from dataclasses import dataclass
from typing import Dict, Union

from ...pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/avatar/Layer.ts
# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/avatar/Avatar.ts
@dataclass
class Layer:
    id: int = 0
    scale: int = 0
    angle: int = 0
    x: int = 0
    y: int = 0
    flip_x: int = 0
    flip_y: int = 0
    color: int = 0

    @staticmethod
    def from_buffer(buffer: ByteBuffer) -> Union['Layer', None]:
        if buffer.read_uint8() != 10:
            return None
        if buffer.read_uint8() == 7:
            buffer.read_uint8()
            buffer.read_uint8()
            buffer.read_uint8()
        buffer.read_int16()
        layer = Layer()
        layer.id = buffer.read_uint16()
        layer.scale = buffer.read_float32()
        layer.angle = buffer.read_float32()
        layer.x = buffer.read_float32()
        layer.y = buffer.read_float32()
        layer.flip_x = buffer.read_bool()
        layer.flip_y = buffer.read_bool()
        layer.color = buffer.read_int32()
        return layer

    @staticmethod
    def from_json(data: Dict) -> 'Layer':
        layer = Layer()
        layer.id = data['id']
        layer.scale = data['scale']
        layer.angle = data['angle']
        layer.x = data['x']
        layer.y = data['y']
        layer.flip_x = data['flipX']
        layer.flip_y = data['flipY']
        layer.color = data['color']
        return layer

    def to_json(self) -> Dict:
        return {
            'id': self.id,
            'scale': self.scale,
            'angle': self.angle,
            'x': self.x,
            'y': self.y,
            'flip_x': self.flip_x,
            'flip_y': self.flip_y,
            'color': self.color,
        }
