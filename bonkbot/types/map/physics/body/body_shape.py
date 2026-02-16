from attrs import define, field

from .....utils.validation import (
    validate_bool,
    validate_float,
    validate_str,
    validate_type,
)
from ..collide import CollideFlag, CollideGroup
from .body_type import BodyType


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IBodyShape.ts
@define(slots=True, auto_attribs=True)
class BodyShape:
    body_type: 'BodyType' = field(
        default=BodyType.STATIC,
        validator=validate_type(BodyType),
    )
    name: str = field(default='Unnamed', validator=validate_str(30))

    density: float = field(
        default=0.3,
        converter=float,
        validator=validate_float(-99999, 99999),
    )
    restitution: float = field(
        default=0.8,
        converter=float,
        validator=validate_float(-99999, 99999),
    )
    friction: float = field(
        default=0.3,
        converter=float,
        validator=validate_float(-99999, 99999),
    )

    linear_damping: float = field(
        default=0.0,
        converter=float,
        validator=validate_float(-99999, 99999),
    )
    angular_damping: float = field(
        default=0.0,
        converter=float,
        validator=validate_float(-99999, 99999),
    )
    fixed_rotation: bool = field(default=False, validator=validate_bool())

    friction_players: bool = field(default=False, validator=validate_bool())
    anti_tunnel: bool = field(default=False, validator=validate_bool())

    collide_mask: 'CollideFlag' = field(
        default=CollideFlag.ALL,
        validator=validate_type(CollideFlag),
    )
    collide_group: 'CollideGroup' = field(
        default=CollideGroup.A,
        validator=validate_type(CollideGroup),
    )

    def to_json(self) -> dict:
        return {
            'type': self.body_type.value,
            'n': self.name,
            'fricp': self.friction_players,
            'ld': self.linear_damping,
            'ad': self.angular_damping,
            'de': self.density,
            'fric': self.friction,
            're': self.restitution,
            'fr': self.fixed_rotation,
            'bu': self.anti_tunnel,
            'f_1': (self.collide_mask & CollideFlag.A) != 0,
            'f_2': (self.collide_mask & CollideFlag.B) != 0,
            'f_3': (self.collide_mask & CollideFlag.C) != 0,
            'f_4': (self.collide_mask & CollideFlag.D) != 0,
            'f_p': (self.collide_mask & CollideFlag.PLAYERS) != 0,
            'f_c': self.collide_group,
        }

    def from_json(self, data: dict) -> 'BodyShape':
        self.body_type = BodyType.from_name(data['type'])
        self.name = data['n']
        self.friction_players = data['fricp']
        self.linear_damping = data['ld']
        self.angular_damping = data['ad']
        self.density = data['de']
        self.friction = data['fric']
        self.restitution = data['re']
        self.fixed_rotation = data['fr']
        self.anti_tunnel = data['bu']
        self.collide_group = CollideGroup.from_id(data['f_c'])
        self.collide_mask = CollideFlag.NONE
        if data['f_1']:
            self.collide_mask |= CollideFlag.A
        if data['f_2']:
            self.collide_mask |= CollideFlag.B
        if data['f_3']:
            self.collide_mask |= CollideFlag.C
        if data['f_4']:
            self.collide_mask |= CollideFlag.D
        if data['f_p']:
            self.collide_mask |= CollideFlag.PLAYERS
        return self
