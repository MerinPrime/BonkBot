from typing import TYPE_CHECKING, Tuple

from attrs import define, field

from .....utils.validation import convert_to_float_vector, validate_vector_range

if TYPE_CHECKING:
    from .....pson.bytebuffer import ByteBuffer


@define(slots=True, auto_attribs=True)
class Shape:
    position: Tuple[float, float] = field(
        default=(0, 0),
        converter=convert_to_float_vector,
        validator=validate_vector_range(-99999, 99999),
    )

    def to_json(self) -> dict: ...

    def from_json(self, data: dict) -> 'Shape': ...

    def to_buffer(self, buffer: 'ByteBuffer') -> None: ...

    def from_buffer(self, buffer: 'ByteBuffer') -> 'Shape': ...
