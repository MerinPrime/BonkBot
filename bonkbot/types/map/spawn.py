from typing import TYPE_CHECKING, Optional, Tuple

from attrs import define, field

from ...utils.validation import (
    convert_to_float_vector,
    validate_bool,
    validate_int,
    validate_opt_bool,
    validate_str,
    validate_vector_range,
)

if TYPE_CHECKING:
    from ...pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/ISpawn.ts
@define(slots=True, auto_attribs=True)
class Spawn:
    name: str = field(default='Spawn', validator=validate_str(59))
    ffa: bool = field(default=True, validator=validate_bool())
    blue: bool = field(default=True, validator=validate_bool())
    red: bool = field(default=True, validator=validate_bool())
    green: Optional[bool] = field(default=None, validator=validate_opt_bool())
    yellow: Optional[bool] = field(default=None, validator=validate_opt_bool())
    priority: int = field(default=5, validator=validate_int(0, 10000))
    position: Tuple[float, float] = field(
        default=(400.0, 300.0),
        converter=convert_to_float_vector,
        validator=validate_vector_range(-10000, 10000),
    )
    velocity: Tuple[float, float] = field(
        default=(0.0, 0.0),
        converter=convert_to_float_vector,
        validator=validate_vector_range(-10000, 10000),
    )

    def to_json(self) -> dict:
        data = {
            'n': self.name,
            'f': self.ffa,
            'b': self.blue,
            'r': self.red,
            'priority': self.priority,
            'x': self.position[0],
            'y': self.position[1],
            'xv': self.velocity[0],
            'yv': self.velocity[1],
        }
        if self.green is not None:
            data['gr'] = self.green
        if self.yellow is not None:
            data['ye'] = self.yellow
        return data

    def from_json(self, data: dict) -> 'Spawn':
        self.name = data['n']
        self.ffa = data['f']
        self.blue = data['b']
        self.red = data['r']
        self.priority = data['priority']
        self.position = (data['x'], data['y'])
        self.velocity = (data['xv'], data['yv'])
        if data.get('gr') is not None:
            self.green = data['gr']
        if data.get('ye') is not None:
            self.yellow = data['ye']
        return self

    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_float64(self.position[0])
        buffer.write_float64(self.position[1])
        buffer.write_float64(self.velocity[0])
        buffer.write_float64(self.velocity[1])
        buffer.write_int16(self.priority)
        buffer.write_bool(self.red)
        buffer.write_bool(self.ffa)
        buffer.write_bool(self.blue)
        buffer.write_bool(self.green)
        buffer.write_bool(self.yellow)
        buffer.write_utf(self.name)

    def from_buffer(self, buffer: 'ByteBuffer') -> 'Spawn':
        self.position = (buffer.read_float64(), buffer.read_float64())
        self.velocity = (buffer.read_float64(), buffer.read_float64())
        self.priority = buffer.read_int16()
        self.red = buffer.read_bool()
        self.ffa = buffer.read_bool()
        self.blue = buffer.read_bool()
        self.green = buffer.read_bool()
        self.yellow = buffer.read_bool()
        self.name = buffer.read_utf()
        return self
