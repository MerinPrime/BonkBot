from typing import List, Union

from attrs import define, field

from ...pson.bytebuffer import ByteBuffer
from .layer import Layer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/avatar/Avatar.ts
@define(slots=True, auto_attribs=True)
class Avatar:
    layers: List['Layer'] = field(factory=list)
    base_color: int = field(default=0x448AFF)

    @staticmethod
    def from_buffer(buffer: 'ByteBuffer') -> 'Avatar':
        avatar = Avatar()
        if buffer.size == 0:
            return avatar
        layers = [None] * 16
        buffer.read_bytes(4)
        version = buffer.read_int16()
        buffer.read_uint8()
        layer_count = (buffer.read_uint8() - 1) // 2
        marker = buffer.read_uint8()
        while marker != 1:
            index = 0
            if marker == 3:
                index = buffer.read_uint8() - 48
            elif marker == 5:
                index = (buffer.read_uint8() - 48) * 10 + (buffer.read_uint8() - 48)
            layers[index] = Layer.from_buffer(buffer)
            marker = buffer.read_uint8()
        for i in range(layer_count):
            layers[i] = Layer.from_buffer(buffer)
        avatar.layers = list(filter(lambda x: x is not None, layers))
        if version >= 2:
            avatar.base_color = buffer.read_int32()
        return avatar

    def to_buffer(self, buffer: Union['ByteBuffer', None] = None) -> 'ByteBuffer':
        if buffer is None:
            buffer = ByteBuffer()

        buffer.write_uint8(0x0A)
        buffer.write_uint8(0x07)
        buffer.write_uint8(0x03)
        buffer.write_uint8(0x61)
        buffer.write_int16(0x02)
        buffer.write_uint8(0x09)
        buffer.write_uint8(len(self.layers) * 2 + 1)
        buffer.write_uint8(0x01)

        for i, layer in enumerate(self.layers):
            buffer.write_uint8(0x0A)

            if i == 0:
                buffer.write_uint8(0x07)
                buffer.write_uint8(0x05)
                buffer.write_uint8(0x61)
                buffer.write_uint8(0x6C)
            else:
                buffer.write_uint8(0x05)

            buffer.write_int16(1)
            buffer.write_int16(layer.id)
            buffer.write_float32(layer.scale)
            buffer.write_float32(layer.angle)
            buffer.write_float32(layer.x)
            buffer.write_float32(layer.y)
            buffer.write_bool(layer.flip_x)
            buffer.write_bool(layer.flip_y)
            buffer.write_int32(layer.color)

        buffer.write_int32(self.base_color)

        return buffer

    @staticmethod
    def from_json(data: dict) -> 'Avatar':
        avatar = Avatar()
        avatar.base_color = data['bc']
        avatar.layers = [
            Layer.from_json(layer) if layer is not None else None
            for layer in data['layers']
        ]
        return avatar

    def to_json(self) -> dict:
        return {
            'bc': self.base_color,
            'layers': [layer.to_json() for layer in self.layers],
        }
