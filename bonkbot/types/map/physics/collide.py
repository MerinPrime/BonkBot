import enum


class CollideFlag(enum.IntFlag):
    NONE = 0
    A = 1
    B = 2
    C = 4
    D = 8
    PLAYERS = 16
    ALL = PLAYERS | A | B | C | D


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
