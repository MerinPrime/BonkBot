import enum
from typing import TypedDict

from attrs import define, field


class InputFlag(enum.IntFlag):
    NONE = 0
    LEFT = 1
    RIGHT = 2
    UP = 4
    DOWN = 8
    HEAVY = 16
    SPECIAL = 32
    ALL = LEFT | RIGHT | UP | DOWN | HEAVY | SPECIAL


class InputsJSON(TypedDict):
    left: bool
    right: bool
    up: bool
    down: bool
    action: bool
    action2: bool


@define(slots=True, auto_attribs=True, frozen=True)
class Inputs:
    left: bool = field(default=False)
    right: bool = field(default=False)
    up: bool = field(default=False)
    down: bool = field(default=False)
    heavy: bool = field(default=False)
    special: bool = field(default=False)

    @property
    def flags(self) -> int:
        flags = InputFlag.NONE
        if self.left:
            flags |= InputFlag.LEFT
        if self.right:
            flags |= InputFlag.RIGHT
        if self.up:
            flags |= InputFlag.UP
        if self.down:
            flags |= InputFlag.DOWN
        if self.heavy:
            flags |= InputFlag.HEAVY
        if self.special:
            flags |= InputFlag.SPECIAL
        return flags

    @classmethod
    def from_flags(cls, flags: int) -> 'Inputs':
        return cls(
            left=bool(flags & InputFlag.LEFT),
            right=bool(flags & InputFlag.RIGHT),
            up=bool(flags & InputFlag.UP),
            down=bool(flags & InputFlag.DOWN),
            heavy=bool(flags & InputFlag.HEAVY),
            special=bool(flags & InputFlag.SPECIAL),
        )

    def to_json(self) -> 'InputsJSON':
        return {
            'left': self.left,
            'right': self.right,
            'up': self.up,
            'down': self.down,
            'action': self.heavy,
            'action2': self.special,
        }

    @classmethod
    def from_json(cls, data: 'InputsJSON') -> 'Inputs':
        return cls(
            left=data['left'],
            right=data['right'],
            up=data['up'],
            down=data['down'],
            heavy=data['action'],
            special=data['action2'],
        )
