from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from bonkbot.core import BonkBot
    from bonkbot.types import Mode

@dataclass(frozen=True)
class RoomInfo:
    bot: "BonkBot"
    name: str
    dbid: int
    players: int
    max_players: int
    has_password: bool
    mode: "Mode"
    min_level: Union[int, None]
    max_level: Union[int, None]
