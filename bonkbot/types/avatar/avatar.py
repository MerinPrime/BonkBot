from typing import TYPE_CHECKING, List

from attrs import define, field

from ...utils.validation import validate_int, validate_type_list
from .layer import Layer

if TYPE_CHECKING:
    from ...pson.bytebuffer import ByteBuffer

# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/avatar/Avatar.ts
@define(slots=True, auto_attribs=True)
class Avatar:
    layers: List['Layer'] = field(factory=list, validator=validate_type_list(Layer, 16))
    base_color: int = field(default=0x448aff, validator=validate_int(0, 16777215))

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

    @staticmethod
    def from_json(data: dict) -> 'Avatar':
        avatar = Avatar()
        avatar.base_color = data['bc']
        avatar.layers = [Layer.from_json(layer) if layer is not None else None
                         for layer in data['layers']]
        return avatar

    def to_json(self) -> dict:
        return {
            'bc': self.base_color,
            'layers': [layer.to_json()
                       for layer in self.layers],
        }
