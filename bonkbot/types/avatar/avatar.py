from dataclasses import dataclass, field
from typing import Dict, List

from ...pson.bytebuffer import ByteBuffer
from .layer import Layer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/avatar/Avatar.ts
@dataclass
class Avatar:
    layers: List[Layer] = field(default_factory=list)
    base_color: int = 0x448aff

    @staticmethod
    def from_buffer(buffer: ByteBuffer) -> 'Avatar':
        avatar = Avatar()
        if buffer.size == 0:
            return avatar
        avatar.layers = [None] * 16
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
            avatar.layers[index] = Layer.from_buffer(buffer)
            marker = buffer.read_uint8()
        for i in range(layer_count):
            avatar.layers[i] = Layer.from_buffer(buffer)
        if version >= 2:
            avatar.base_color = buffer.read_int32()
        return avatar

    @staticmethod
    def from_json(data: Dict) -> 'Avatar':
        avatar = Avatar()
        avatar.base_color = data['bc']
        avatar.layers = [Layer.from_json(layer) for layer in data['layers']]
        return avatar

    def to_json(self) -> Dict:
        return {
            'bc': self.base_color,
            'layers': [layer.to_json() for layer in self.layers],
        }
