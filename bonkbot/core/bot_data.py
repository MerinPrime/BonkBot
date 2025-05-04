from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Union

if TYPE_CHECKING:
    from bonkbot.types.avatar.avatar import Avatar
    from bonkbot.types.friend import Friend
    from bonkbot.types.settings import Settings


@dataclass
class BotData:
    name: str = ''
    token: str = ''
    dbid: Union[int, None] = None
    xp: Union[int, None] = None
    avatar: "Avatar" = None
    active_avatar: int = 0
    avatars: List["Avatar"] = field(default_factory=list)
    friends: List["Friend"] = field(default_factory=list)
    legacy_friends: List["Friend"] = field(default_factory=list)
    settings: "Settings" = None
