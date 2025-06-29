import enum
from typing import TYPE_CHECKING, Optional

import attrs

from bonkbot.utils.validation import validate_length

if TYPE_CHECKING:
    from bonkbot.pson import ByteBuffer


class CaptureType(enum.IntEnum):
    NORMAL = 1
    INSTANT_RED = 2
    INSTANT_BLUE = 3
    INSTANT_GREEN = 4
    INSTANT_YELLOW = 5

    @staticmethod
    def from_id(type_id: int) -> 'CaptureType':
        for capture_type in CaptureType:
            if type_id == capture_type.value:
                return capture_type


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/ICapZone.ts
@attrs.define(slots=True, auto_attribs=True)
class CaptureZone:
    name: str = attrs.field(default='Cap Zone', validator=attrs.validators.and_(
        attrs.validators.instance_of(str),
        validate_length(30)
    ))
    shape_id: int = attrs.field(default=-1, validator=attrs.validators.optional(attrs.validators.ge(-1)))
    seconds: float = attrs.field(default=10, converter=float, validator=attrs.validators.and_(
        attrs.validators.ge(0.01),
        attrs.validators.le(1000)
    ))
    type: 'CaptureType' = attrs.field(default=CaptureType.NORMAL, validator=attrs.validators.instance_of(CaptureType))
    
    def to_json(self) -> dict:
        data = {
            'i': self.shape_id,
            'l': self.seconds,
            'n': self.name,
        }
        if self.type is not None:
            data['ty'] = self.type.value
        return data

    def from_json(self, data: dict) -> 'CaptureZone':
        self.name = data['n']
        self.seconds = data['l']
        self.shape_id = data['i']
        self.type = data.get('ty', CaptureType.NORMAL)
        return self
    
    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_utf(self.name)
        buffer.write_float64(self.seconds)
        buffer.write_int16(self.shape_id)
        buffer.write_int16(self.type.value)
    
    def from_buffer(self, buffer: 'ByteBuffer', version: int) -> 'CaptureZone':
        self.name = buffer.read_utf()
        self.seconds = buffer.read_float64()
        self.shape_id = buffer.read_int16()
        if version >= 6:
            self.type = CaptureType.from_id(buffer.read_int16())
        return self
