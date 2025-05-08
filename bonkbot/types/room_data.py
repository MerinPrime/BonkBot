from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Union

from .mode import Mode
from .team import TeamState

if TYPE_CHECKING:
    from ..core.player import Player

@dataclass
class RoomData:
    name: str
    host: 'Player'
    id: int = 0
    mode: 'Mode' = Mode.CLASSIC
    players: List['Player'] = field(default_factory=list)
    password: Union[str, None] = None
    rounds: int = 3
    team_state: 'TeamState' = TeamState.FFA
    team_lock: bool = False
    join_id: Union[str, None] = None
    join_bypass: str = ''

    def player_by_id(self, player_id: int) -> 'Player':
        for player in self.players:
            if player.id == player_id:
                return player
        return None
