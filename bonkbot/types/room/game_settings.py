from typing import List

import attrs

from ...utils.validation import (
    validate_bool,
    validate_int,
    validate_int_list,
    validate_type,
)
from ..map.bonkmap import BonkMap
from ..mode import Mode
from ..team import TeamState


@attrs.define(slots=True, auto_attribs=True)
class GameSettings:
    map: 'BonkMap' = attrs.field(factory=BonkMap, validator=validate_type(BonkMap))
    is_quick_play: bool = attrs.field(default=False, validator=validate_bool())
    rounds: int = attrs.field(default=3, validator=validate_int(1))
    team_lock: bool = attrs.field(default=False, validator=validate_bool())
    team_state: TeamState = attrs.field(default=TeamState.FFA, validator=validate_type(TeamState))
    mode: Mode = attrs.field(default=Mode.CLASSIC, validator=validate_type(Mode))
    balance: List[int] = attrs.field(factory=list, validator=validate_int_list(-100, 100))
    
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
        self.is_quick_play = data['q'] == ('bonkquick', True)
        self.team_lock = data['tl']
        if data['tea']:
            self.team_state = TeamState.TEAMS
        else:
            self.team_state = TeamState.FFA
        self.mode = Mode.from_mode_code(data['mo'])
        self.balance = data['bal']
