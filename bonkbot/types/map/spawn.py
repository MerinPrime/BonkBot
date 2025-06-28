from typing import Optional, Tuple

import attrs

from ...utils.validation import validate_vector_range, convert_to_float_vector


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/ISpawn.ts
@attrs.define(slots=True, auto_attribs=True)
class Spawn:
    name: str = attrs.field(default='Spawn', validator=attrs.validators.instance_of(str))
    ffa: bool = attrs.field(default=True, validator=attrs.validators.instance_of(bool))
    blue: bool = attrs.field(default=True, validator=attrs.validators.instance_of(bool))
    red: bool = attrs.field(default=True, validator=attrs.validators.instance_of(bool))
    green: Optional[bool] = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(bool)))
    yellow: Optional[bool] = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(bool)))
    priority: float = attrs.field(default=5, converter=float, validator=attrs.validators.and_(
        attrs.validators.ge(0),
        attrs.validators.le(10000),
    ))
    position: Tuple[float, float] = attrs.field(default=(400.0, 300.0),
                                                converter=convert_to_float_vector,
                                                validator=validate_vector_range(-10000, 10000))
    velocity: Tuple[float, float] = attrs.field(default=(0.0, 0.0),
                                                converter=convert_to_float_vector,
                                                validator=validate_vector_range(-10000, 10000))
