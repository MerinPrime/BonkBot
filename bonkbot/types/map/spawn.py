from typing import TYPE_CHECKING, Optional, Tuple

import attrs

from ...utils.validation import convert_to_float_vector, validate_vector_range

if TYPE_CHECKING:
    from ...pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/ISpawn.ts
@attrs.define(slots=True, auto_attribs=True)
class Spawn:
    name: str = attrs.field(default='Spawn', validator=attrs.validators.instance_of(str))
    ffa: bool = attrs.field(default=True, validator=attrs.validators.instance_of(bool))
    blue: bool = attrs.field(default=True, validator=attrs.validators.instance_of(bool))
    red: bool = attrs.field(default=True, validator=attrs.validators.instance_of(bool))
    green: Optional[bool] = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(bool)))
    yellow: Optional[bool] = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(bool)))
    priority: int = attrs.field(default=5, validator=attrs.validators.and_(
        attrs.validators.instance_of(int),
        attrs.validators.ge(0),
        attrs.validators.le(10000),
    ))
    position: Tuple[float, float] = attrs.field(default=(400.0, 300.0),
                                                converter=convert_to_float_vector,
                                                validator=validate_vector_range(-10000, 10000))
    velocity: Tuple[float, float] = attrs.field(default=(0.0, 0.0),
                                                converter=convert_to_float_vector,
                                                validator=validate_vector_range(-10000, 10000))
    
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
    
    @staticmethod
    def from_json(data: dict) -> 'Spawn':
        spawn = Spawn()
        spawn.name = data['n']
        spawn.ffa = data['f']
        spawn.blue = data['b']
        spawn.red = data['r']
        spawn.priority = data['priority']
        spawn.position = (data['x'], data['y'])
        spawn.velocity = (data['xv'], data['yv'])
        if data.get('gr') is not None:
            spawn.green = data['gr']
        if data.get('ye') is not None:
            spawn.yellow = data['ye']
        return spawn
    
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

    @staticmethod
    def from_buffer(buffer: 'ByteBuffer') -> 'Spawn':
        spawn = Spawn()
        spawn.position = (buffer.read_float64(), buffer.read_float64())
        spawn.velocity = (buffer.read_float64(), buffer.read_float64())
        spawn.priority = buffer.read_int16()
        spawn.red = buffer.read_bool()
        spawn.ffa = buffer.read_bool()
        spawn.blue = buffer.read_bool()
        spawn.green = buffer.read_bool()
        spawn.yellow = buffer.read_bool()
        spawn.name = buffer.read_utf()
        return spawn
