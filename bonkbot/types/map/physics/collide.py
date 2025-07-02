import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....pson.bytebuffer import ByteBuffer


class CollideFlag(enum.IntFlag):
    NONE = 0
    A = 1
    B = 2
    C = 4
    D = 8
    PLAYERS = 16
    ALL = PLAYERS | A | B | C | D

    def to_buffer(self, buffer: 'ByteBuffer') -> None:
        buffer.write_bool(self & CollideFlag.A != 0)
        buffer.write_bool(self & CollideFlag.B != 0)
        buffer.write_bool(self & CollideFlag.C != 0)
        buffer.write_bool(self & CollideFlag.D != 0)
        buffer.write_bool(self & CollideFlag.PLAYERS != 0)

    @staticmethod
    def from_buffer(buffer: 'ByteBuffer', version: int) -> 'CollideFlag':
        mask = CollideFlag.NONE
        if buffer.read_bool():
            mask = mask | CollideFlag.A
        if buffer.read_bool():
            mask = mask | CollideFlag.B
        if buffer.read_bool():
            mask = mask | CollideFlag.C
        if buffer.read_bool():
            mask = mask | CollideFlag.D
        if version >= 2 and buffer.read_bool():
            mask = mask | CollideFlag.PLAYERS
        return mask


class CollideGroup(enum.IntEnum):
    A = 1
    B = 2
    C = 4
    D = 8

    @classmethod
    def from_id(cls, group: int) -> 'CollideGroup':
        for collide_group in CollideGroup:
            if collide_group == group:
                return collide_group
