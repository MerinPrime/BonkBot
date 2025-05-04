import math


def xp_to_level(xp: int) -> float:
    return xp ** 0.5 / 10 + 1


def level_to_xp(level: int) -> int:
    return ((level - 1) * 10) ** 2
