from typing import TYPE_CHECKING, List, Optional, Tuple

from attrs import define, field

from ..collide import CollideFlag, CollideGroup
from .body_force import BodyForce
from .body_shape import BodyShape
from .body_type import BodyType
from .force_zone import ForceZone

if TYPE_CHECKING:
    from .....pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IBody.ts
@define(slots=True, auto_attribs=True)
class Body:
    name: Optional[str] = field(default=None)  # 30

    position: Tuple[float, float] = field(default=(0, 0))  # -99999,+99999
    linear_velocity: Tuple[float, float] = field(default=(0, 0))  # -99999,+99999
    angle: float = field(default=0.0)  # -9999,+9999
    angular_velocity: float = field(default=0.0)  # -9999,+9999

    fixtures: List[int] = field(factory=list)  # 32767
    shape: 'BodyShape' = field(factory=BodyShape)
    force: 'BodyForce' = field(factory=BodyForce)
    force_zone: 'ForceZone' = field(factory=ForceZone)

    def to_json(self) -> dict:
        data = {
            'a': self.angle,
            'av': self.angular_velocity,
            'fx': self.fixtures,
            'p': self.position,
            'lv': self.linear_velocity,
            'cf': self.force.to_json(),
            'fz': self.force_zone.to_json(),
            's': self.shape.to_json(),
        }
        if self.name is not None:
            data['n'] = self.name
        return data

    def from_json(self, data: dict) -> 'Body':
        if data.get('n') is not None:
            self.name = data['n']
        self.angle = data['a']
        self.angular_velocity = data['av']
        self.fixtures = data['fx']
        self.position = (data['p'][0], data['p'][1])
        self.linear_velocity = (data['lv'][0], data['lv'][1])
        self.force.from_json(data['cf'])
        self.force_zone.from_json(data['fz'])
        self.shape.from_json(data['s'])
        return self

    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_utf(self.shape.body_type.value)
        buffer.write_utf(self.shape.name)
        buffer.write_float64(self.position[0])
        buffer.write_float64(self.position[1])
        buffer.write_float64(self.angle)
        buffer.write_float64(self.shape.friction)
        buffer.write_bool(self.shape.friction_players)
        buffer.write_float64(self.shape.restitution)
        buffer.write_float64(self.shape.density)
        buffer.write_float64(self.linear_velocity[0])
        buffer.write_float64(self.linear_velocity[1])
        buffer.write_float64(self.angular_velocity)
        buffer.write_float64(self.shape.linear_damping)
        buffer.write_float64(self.shape.angular_damping)
        buffer.write_bool(self.shape.fixed_rotation)
        buffer.write_bool(self.shape.anti_tunnel)
        self.force.to_buffer(buffer)
        buffer.write_int16(self.shape.collide_group.value)
        self.shape.collide_mask.to_buffer(buffer)
        self.force_zone.to_buffer(buffer)
        buffer.write_int16(len(self.fixtures))
        for fixture in self.fixtures:
            buffer.write_int16(fixture)

    def from_buffer(self, buffer: 'ByteBuffer', version: int) -> 'Body':
        self.shape.body_type = BodyType.from_name(buffer.read_utf())
        self.shape.name = buffer.read_utf()
        self.position = (buffer.read_float64(), buffer.read_float64())
        self.angle = buffer.read_float64()
        self.shape.friction = buffer.read_float64()
        self.shape.friction_players = buffer.read_bool()
        self.shape.restitution = buffer.read_float64()
        self.shape.density = buffer.read_float64()
        self.linear_velocity = (buffer.read_float64(), buffer.read_float64())
        self.angular_velocity = buffer.read_float64()
        self.shape.linear_damping = buffer.read_float64()
        self.shape.angular_damping = buffer.read_float64()
        self.shape.fixed_rotation = buffer.read_bool()
        self.shape.anti_tunnel = buffer.read_bool()
        self.force.from_buffer(buffer)
        self.shape.collide_group = CollideGroup.from_id(buffer.read_int16())
        self.shape.collide_mask = CollideFlag.from_buffer(buffer, version)
        if version >= 14:
            self.force_zone.from_buffer(buffer, version)
        fixtures_count = buffer.read_int16()
        for _ in range(fixtures_count):
            self.fixtures.append(buffer.read_int16())
        return self
