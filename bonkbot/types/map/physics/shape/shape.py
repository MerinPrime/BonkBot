from typing import TYPE_CHECKING, Tuple

from attrs import define, field

if TYPE_CHECKING:
    from .....pson.bytebuffer import ByteBuffer


@define(slots=True, auto_attribs=True)
class Shape:
    position: Tuple[float, float] = field(default=(0, 0))  # -99999,+99999

    def to_json(self) -> dict: ...

    def from_json(self, data: dict) -> 'Shape': ...

    def to_buffer(self, buffer: 'ByteBuffer') -> None: ...

    def from_buffer(self, buffer: 'ByteBuffer') -> 'Shape': ...
