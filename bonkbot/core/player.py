import dataclasses
from typing import TYPE_CHECKING, Union


if TYPE_CHECKING:
    from peerjs_py.dataconnection.BufferedConnection.BinaryPack import BinaryPack

    from ..types.avatar import Avatar
    from ..types.team import Team
    from .bonkbot import BonkBot
    from .room import Room

@dataclasses.dataclass
class Player:
    bot: 'BonkBot'
    room: 'Room'
    data_connection: Union['BinaryPack', None]
    id: int
    team: 'Team'
    avatar: 'Avatar'
    name: str
    is_guest: bool
    ready: bool
    tabbed: bool
    level: int
    peer_id: str = ''
    ping: int = 105
    joined_with_bypass: Union[bool, None] = None

    @property
    def is_bot(self) -> bool:
        return self.room.bot == self

    @property
    def is_host(self) -> bool:
        return self.room.host == self
