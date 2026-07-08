import math


def xp_to_level(xp: int) -> float:
    return math.sqrt(xp) / 10 + 1


def level_to_xp(level: int) -> int:
    return ((level - 1) * 10) ** 2
