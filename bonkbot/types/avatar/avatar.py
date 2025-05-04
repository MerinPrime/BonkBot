from dataclasses import dataclass, field
from typing import List

from bonkbot.pson import ByteBuffer
from bonkbot.types.avatar.layer import Layer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/avatar/Avatar.ts
@dataclass
class Avatar:
    layers: List[Layer] = field(default_factory=list)
    baseColor: int = 0x448aff

    @staticmethod
    def from_buffer(buffer: ByteBuffer) -> "Avatar":
        avatar = Avatar()
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
            avatar.baseColor = buffer.read_int32()
        return avatar
