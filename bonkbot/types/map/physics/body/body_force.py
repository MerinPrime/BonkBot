from typing import TYPE_CHECKING, Tuple

from attrs import define, field

from .....utils.validation import (
    convert_to_float_vector,
    validate_bool,
    validate_float,
    validate_vector_range,
)

if TYPE_CHECKING:
    from .....pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IBodyForce.ts
@define(slots=True, auto_attribs=True)
class BodyForce:
    force: Tuple[float, float] = field(default=(0, 0), converter=convert_to_float_vector,
                                       validator=validate_vector_range(-999999, 999999))
    is_relative: bool = field(default=True, validator=validate_bool())
    torque: float = field(default=0, converter=float, validator=validate_float(-999999, 999999))

    def to_json(self) -> dict:
        return {
            'x': self.force[0],
            'y': self.force[1],
            'ct': self.torque,
            'w': self.is_relative,
        }

    def from_json(self, data: dict) -> 'BodyForce':
        self.force = (data['x'], data['y'])
        self.torque = data['ct']
        self.is_relative = data['w']
        return self

    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_float64(self.force[0])
        buffer.write_float64(self.force[1])
        buffer.write_float64(self.torque)
        buffer.write_bool(self.is_relative)

    def from_buffer(self, buffer: 'ByteBuffer') -> 'BodyForce':
        self.force = (buffer.read_float64(), buffer.read_float64())
        self.torque = buffer.read_float64()
        self.is_relative = buffer.read_bool()
        return self
