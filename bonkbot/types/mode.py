import enum

from bonkbot.types.gamo import GaMo


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/GameSettings.ts
class Mode(enum.Enum):
    CLASSIC = GaMo('b', 'b')
    SIMPLE = GaMo('b', 'bs')
    ARROWS = GaMo('b', 'ar')
    DEATH_ARROWS = GaMo('b', 'ard')
    GRAPPLE = GaMo('b', 'sp')
    VTOL = GaMo('b', 'v')
    FOOTBALL = GaMo('f', 'f')

    @property
    def engine(self) -> str:
        return self.value.engine

    @property
    def mode(self) -> str:
        return self.value.mode

    @staticmethod
    def from_mode_code(string: str) -> "Mode":
        for mode in Mode:
            if mode.mode == string:
                return mode
        raise ValueError(f'Invalid mode code: {string}')
