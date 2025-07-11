from typing import Optional

from attrs import define, field

from ..utils.validation import validate_opt_int, validate_str


@define(slots=True, auto_attribs=True, frozen=True)
class Friend:
    name: str = field(validator=validate_str(15))
    dbid: Optional[int] = field(default=None, validator=validate_opt_int(0))
    room_id: Optional[int] = field(default=None, validator=validate_opt_int(0))
