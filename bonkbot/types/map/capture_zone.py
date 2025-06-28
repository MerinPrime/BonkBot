import enum
from dataclasses import dataclass
from typing import TYPE_CHECKING

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
@dataclass
class CaptureZone:
    name: str = 'Cap Zone'
    shape_id: int = -1
    seconds: float = 10
    type: 'CaptureType' = CaptureType.NORMAL
    
    def to_json(self) -> dict:
        data = {
            'i': self.shape_id,
            'l': self.seconds,
            'n': self.name,
        }
        if self.type is not None:
            data['ty'] = self.type.value
        return data

    @staticmethod
    def from_json(data: dict) -> 'CaptureZone':
        capture_zone = CaptureZone()
        capture_zone.name = data['n']
        capture_zone.seconds = data['l']
        capture_zone.shape_id = data['i']
        capture_zone.type = data.get('ty', CaptureType.NORMAL)
        return capture_zone
    
    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_utf(self.name)
        buffer.write_float64(self.seconds)
        buffer.write_int16(self.shape_id)
        buffer.write_int16(self.type.value)
    
    @staticmethod
    def from_buffer(buffer: 'ByteBuffer', version: int) -> 'CaptureZone':
        capture_zone = CaptureZone()
        capture_zone.name = buffer.read_utf()
        capture_zone.seconds = buffer.read_float64()
        capture_zone.shape_id = buffer.read_int16()
        if version >= 6:
            capture_zone.type = CaptureType.from_id(buffer.read_int16())
        return capture_zone
