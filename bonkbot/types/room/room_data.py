from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

from ...types.map import BonkMap
from ...types.mode import Mode
from ...types.team import TeamState

if TYPE_CHECKING:
    from ...core.room.player import Player

@dataclass
class RoomData:
    name: str
    password: Optional[str] = None
    join_id: Optional[str] = None
    join_bypass: str = ''
    host: Optional['Player'] = None
    players: List['Player'] = field(default_factory=list)
    map: Optional['BonkMap'] = None
    mode: 'Mode' = Mode.CLASSIC
    team_state: 'TeamState' = TeamState.FFA
    team_lock: bool = False
    rounds: int = 3
    gt: int = 2 # In room 2 in quick play 1 ( Not tested fully )
    is_quick_play: bool = False

    def player_by_id(self, player_id: int) -> 'Player':
        for player in self.players:
            if player.id == player_id:
                return player
        return None

    def get_game_settings(self) -> dict:
        bal = [0] * len(self.players)
        for player in self.players:
            if player.is_left:
                continue
            bal[player.id] = player.balance
        return {
            'map': self.map.to_json(),
            'gt': self.gt,
            'wl': self.rounds,
            'q': self.is_quick_play,
            'tl': self.team_lock,
            'tea': self.team_state != TeamState.FFA,
            'ga': self.mode.engine,
            'mo': self.mode.mode,
            'bal': bal,
        }

    def set_game_settings(self, game_settings: dict) -> None:
        encoded_map = game_settings['map']
        if isinstance(encoded_map, str):
            self.map = BonkMap.decode_from_database(encoded_map)
        elif isinstance(encoded_map, dict):
            self.map = BonkMap.from_json(encoded_map)
        else:
            raise ValueError(f'Invalid map provided: {encoded_map}')
        self.gt = game_settings['gt']
        self.rounds = game_settings['wl']
        self.is_quick_play = game_settings['q']
        self.team_lock = game_settings['tl']
        if not game_settings['tea']:
            self.team_state = TeamState.FFA
        elif self.mode == Mode.FOOTBALL:
            self.team_state = TeamState.DUO
        else:
            self.team_state = TeamState.ALL
        self.mode = Mode.from_mode_code(game_settings['mo'])
        bal = game_settings['bal']
        for player in self.players:
            if player.id >= len(bal):
                player.balance = 0
                continue
            player.balance = bal[player.id]
