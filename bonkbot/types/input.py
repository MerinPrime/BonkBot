import enum
from dataclasses import dataclass


class InputFlag(enum.IntFlag):
    NONE = 0
    LEFT = 1
    RIGHT = 2
    UP = 4
    DOWN = 8
    HEAVY = 16
    SPECIAL = 32
    ALL = LEFT | RIGHT | UP | DOWN | HEAVY | SPECIAL


@dataclass
class Inputs:
    left: bool = False
    right: bool = False
    up: bool = False
    down: bool = False
    heavy: bool = False
    special: bool = False

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

    @flags.setter
    def flags(self, flags: int) -> None:
        self.left = bool(flags & InputFlag.LEFT)
        self.right = bool(flags & InputFlag.RIGHT)
        self.up = bool(flags & InputFlag.UP)
        self.down = bool(flags & InputFlag.DOWN)
        self.heavy = bool(flags & InputFlag.HEAVY)
        self.special = bool(flags & InputFlag.SPECIAL)
