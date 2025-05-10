import dataclasses
from dataclasses import field
from typing import TYPE_CHECKING, Dict, Union

from ..types.errors import ApiError, ErrorType
from ..types.player_move import PlayerMove
from ..types.team import Team
from .api import SocketEvents

if TYPE_CHECKING:
    from peerjs_py.dataconnection.BufferedConnection.BinaryPack import BinaryPack

    from ..types.avatar import Avatar
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
    balance: int = 0
    ping: int = 105
    joined_with_bypass: Union[bool, None] = None
    moves: Dict[str, PlayerMove] = field(default_factory=dict)
    peer_ban_until: float = 0
    peer_ban_level: int = 0
    peer_reverts: int = 0
    is_friend: bool = False

    @property
    def is_bot(self) -> bool:
        return self.room.bot == self

    @property
    def is_host(self) -> bool:
        return self.room.host == self

    async def kick(self) -> None:
        if not self.room.bot_player.is_host:
            await self.bot.dispatch('on_error', ApiError(ErrorType.NOT_HOST))
            return
        await self.room.socket.emit(SocketEvents.Outgoing.BAN, {'banshortid': self.id, 'kickonly': True})

    async def ban(self) -> None:
        if not self.room.bot_player.is_host:
            await self.bot.dispatch('on_error', ApiError(ErrorType.NOT_HOST))
            return
        await self.room.socket.emit(SocketEvents.Outgoing.BAN, {'banshortid': self.id, 'kickonly': False})

    async def change_team(self, new_team: Team) -> None:
        if not self.room.bot_player.is_host:
            await self.bot.dispatch('on_error', ApiError(ErrorType.NOT_HOST))
            return
        await self.room.socket.emit(SocketEvents.Outgoing.SET_BALANCE, {'targetID': self.id, 'targetTeam': new_team})

    async def set_balance(self, new_balance: int) -> None:
        if not self.room.bot_player.is_host:
            await self.bot.dispatch('on_error', ApiError(ErrorType.NOT_HOST))
            return
        if not -100 <= new_balance <= 100:
            await self.bot.dispatch('on_error', ApiError(ErrorType.INVALID_BALANCE))
            return
        await self.room.socket.emit(SocketEvents.Outgoing.SET_BALANCE, {'sid': self.id, 'bal': new_balance})

    async def give_host(self) -> None:
        if not self.room.bot_player.is_host:
            await self.bot.dispatch('on_error', ApiError(ErrorType.NOT_HOST))
            return
        await self.room.socket.emit(SocketEvents.Outgoing.GIVE_HOST, {'id': self.id})

    async def send_friend_request(self) -> None:
        if self.is_friend:
            return
        await self.room.socket.emit(SocketEvents.Outgoing.FRIEND_REQUEST, {'id': self.id})
