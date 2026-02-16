from typing import List

from attrs import define, field

from ..map.bonkmap import BonkMap
from ..mode import Mode
from ..team import TeamState


@define(slots=True, auto_attribs=True)
class GameSettings:
    map: 'BonkMap' = field(factory=BonkMap)
    is_quick_play: bool = field(default=False)
    rounds: int = field(default=3)
    team_lock: bool = field(default=False)
    team_state: 'TeamState' = field(
        default=TeamState.FFA,
    )
    mode: 'Mode' = field(default=Mode.CLASSIC)
    balance: List[int] = field(
        factory=list,
    )

    def to_json(self) -> dict:
        return {
            'map': self.map.to_json(),
            'gt': 1 if self.is_quick_play else 2,
            'wl': self.rounds,
            'q': 'bonkquick' if self.is_quick_play else False,
            'tl': self.team_lock,
            'tea': self.team_state != TeamState.FFA,
            'ga': self.mode.engine,
            'mo': self.mode.mode,
            'bal': self.balance,
        }

    def from_json(self, data: dict) -> None:
        encoded_map = data['map']
        if isinstance(encoded_map, str):
            self.map = BonkMap.decode_from_database(encoded_map)
        elif isinstance(encoded_map, dict):
            self.map = BonkMap.from_json(encoded_map)
        else:
            raise ValueError(f'Invalid map provided: {encoded_map}')
        self.rounds = data['wl']
        self.is_quick_play = data['q'] in ('bonkquick', True)
        self.team_lock = data['tl']
        if data['tea']:
            self.team_state = TeamState.TEAMS
        else:
            self.team_state = TeamState.FFA
        self.mode = Mode.from_mode_code(data['mo'])
        self.balance = data['bal']
