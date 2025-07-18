from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

from bonkbot.core.room import Player

from .game_settings import GameSettings

if TYPE_CHECKING:
    from ...core.room.player import Player


@dataclass
class RoomData:
    name: str
    password: Optional[str] = None
    join_id: Optional[str] = None
    join_bypass: Optional[str] = None
    host: Optional['Player'] = None
    players: List['Player'] = field(default_factory=list)
    game_settings: 'GameSettings' = field(default_factory=GameSettings)

    def player_by_id(self, player_id: int) -> Optional['Player']:
        for player in self.players:
            if player.id == player_id:
                return player
        return None
