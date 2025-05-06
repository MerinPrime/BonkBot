from dataclasses import dataclass
from typing import Union

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
    flipX: int = 0
    flipY: int = 0
    color: int = 0

    @staticmethod
    def from_buffer(buffer: ByteBuffer) -> Union["Layer", None]:
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
        layer.flipX = buffer.read_uint8() == 1
        layer.flipY = buffer.read_uint8() == 1
        layer.color = buffer.read_int32()
        return layer
