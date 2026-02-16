from typing import TYPE_CHECKING

from attrs import define

if TYPE_CHECKING:
    from .....pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IJoint.ts
@define(slots=True, auto_attribs=True)
class Joint:
    def to_json(self) -> dict: ...

    def from_json(self, data: dict) -> 'Joint': ...

    def to_buffer(self, buffer: 'ByteBuffer') -> None: ...

    def from_buffer(self, buffer: 'ByteBuffer') -> 'Joint': ...
