import enum
from dataclasses import dataclass


@dataclass(frozen=True)
class GaMo:
    engine: str
    mode: str

# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/GameSettings.ts
class Mode(enum.Enum):
    CLASSIC = GaMo(engine='b', mode='b')
    SIMPLE = GaMo(engine='b', mode='bs')
    ARROWS = GaMo(engine='b', mode='ar')
    DEATH_ARROWS = GaMo(engine='b', mode='ard')
    GRAPPLE = GaMo(engine='b', mode='sp')
    VTOL = GaMo(engine='b', mode='v')
    FOOTBALL = GaMo(engine='f', mode='f')

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
