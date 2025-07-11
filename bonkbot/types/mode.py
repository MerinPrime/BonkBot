import enum

from attrs import define, field

from ..utils.validation import validate_int, validate_str


@define(slots=True, auto_attribs=True, frozen=True)
class GaMo:
    engine: str = field(validator=validate_str())
    mode: str = field(validator=validate_str())
    id: int = field(validator=validate_int(0))


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/GameSettings.ts
class Mode(enum.Enum):
    NONE = GaMo(engine='', mode='', id=0)
    CLASSIC = GaMo(engine='b', mode='b', id=1)
    SIMPLE = GaMo(engine='b', mode='bs', id=2)
    ARROWS = GaMo(engine='b', mode='ar', id=3)
    DEATH_ARROWS = GaMo(engine='b', mode='ard', id=4)
    GRAPPLE = GaMo(engine='b', mode='sp', id=5)
    VTOL = GaMo(engine='b', mode='v', id=6)
    FOOTBALL = GaMo(engine='f', mode='f', id=7)

    @property
    def engine(self) -> str:
        return self.value.engine

    @property
    def mode(self) -> str:
        return self.value.mode

    @property
    def id(self) -> int:
        return self.value.id

    @staticmethod
    def from_mode_code(string: str) -> 'Mode':
        for mode in Mode:
            if mode.mode == string:
                return mode
        raise ValueError(f'Invalid mode code: {string}')

    @staticmethod
    def from_mode_id(mode_id: int) -> 'Mode':
        for mode in Mode:
            if mode.id == mode_id:
                return mode
        raise ValueError(f'Invalid mode id: {mode_id}')
