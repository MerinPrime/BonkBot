from typing import List

import attrs

from ..map.bonkmap import BonkMap
from ..mode import Mode
from ..team import TeamState


@attrs.define(slots=True, auto_attribs=True)
class GameSettings:
    map: 'BonkMap' = attrs.field(factory=BonkMap)
    is_quick_play: bool = attrs.field(default=False, validator=attrs.validators.instance_of(bool))
    rounds: int = attrs.field(default=3, validator=attrs.validators.and_(
        attrs.validators.instance_of(int),
        attrs.validators.ge(1),
    ))
    team_lock: bool = attrs.field(default=False, validator=attrs.validators.instance_of(bool))
    team_state: TeamState = attrs.field(default=TeamState.FFA, validator=attrs.validators.instance_of(TeamState))
    mode: Mode = attrs.field(default=Mode.CLASSIC, validator=attrs.validators.instance_of(Mode))
    balance: List[int] = attrs.field(factory=list)
    
    def to_json(self) -> dict:
        return {
            'map': self.map.to_json(),
            'gt': 1 if self.is_quick_play else 2,
            'wl': self.rounds,
            'q': self.is_quick_play,
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
        self.is_quick_play = data['q']
        self.team_lock = data['tl']
        if data['tea']:
            self.team_state = TeamState.TEAMS
        else:
            self.team_state = TeamState.FFA
        self.mode = Mode.from_mode_code(data['mo'])
        self.balance = data['bal']
