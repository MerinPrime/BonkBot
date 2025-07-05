from typing import TYPE_CHECKING

from attrs import define, field

from ...utils.validation import (
    validate_float,
    validate_int,
    validate_str,
    validate_type,
)
from .capture_type import CaptureType

if TYPE_CHECKING:
    from ...pson.bytebuffer import ByteBuffer



# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/ICapZone.ts
@define(slots=True, auto_attribs=True)
class CaptureZone:
    name: str = field(default='Cap Zone', validator=validate_str(29))
    shape_id: int = field(default=-1, validator=validate_int(-1))
    seconds: float = field(default=10, converter=float, validator=validate_float(0.01, 1000))
    type: 'CaptureType' = field(default=CaptureType.NORMAL, validator=validate_type(CaptureType))

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
        self.type = CaptureType.from_id(data.get('ty', CaptureType.NORMAL.value))
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
