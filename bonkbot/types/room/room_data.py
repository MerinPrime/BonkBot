from typing import TYPE_CHECKING, List, Optional

from attrs import define, field

from .game_settings import GameSettings

if TYPE_CHECKING:
    from ...core.room.player import Player


@define(slots=True, auto_attribs=True)
class RoomData:
    name: str
    password: Optional[str] = None
    join_id: Optional[str] = None
    join_bypass: Optional[str] = None
    host: Optional['Player'] = None
    players: List['Player'] = field(factory=list)
    game_settings: 'GameSettings' = field(factory=GameSettings)

    def player_by_id(self, player_id: int) -> Optional['Player']:
        for player in self.players:
            if player.id == player_id:
                return player
        return None
