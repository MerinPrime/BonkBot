import asyncio
from typing import TYPE_CHECKING, List, Optional, Union

import aiohttp

from bonkbot.core.bot.bonk_api import BonkAPI
from bonkbot.core.bot_data import BotData
from bonkbot.core.bot_event_handler import BotEventHandler
from bonkbot.core.room import Room
from bonkbot.types import Server
from bonkbot.types.avatar.avatar import Avatar
from bonkbot.types.errors.api_error import ApiError
from bonkbot.types.errors.error_type import ErrorType
from bonkbot.types.errors.not_logged_error import BotNotLoggedInError
from bonkbot.types.friend import Friend
from bonkbot.types.room.room_create_params import RoomCreateParams
from bonkbot.types.room.room_info import RoomInfo
from bonkbot.types.settings import Settings
from bonkbot.utils.api import validate_username
from bonkbot.utils.xp import xp_to_level

if TYPE_CHECKING:
    from bonkbot.types.map import BonkMap
    from bonkbot.types.room.room_join_params import RoomJoinParams


class BonkBot(BotEventHandler):
    def __init__(self, event_loop: Optional[asyncio.AbstractEventLoop] = None,
                 aiohttp_session: Optional[aiohttp.ClientSession] = None):
        super().__init__()
        if event_loop is None:
            event_loop = asyncio.get_event_loop()
        if aiohttp_session is None:
            aiohttp_session = aiohttp.ClientSession(loop=event_loop)
        self._event_loop: asyncio.AbstractEventLoop = event_loop
        self._bonk_api: BonkAPI = BonkAPI(event_loop, aiohttp_session)
        self._data: Optional[BotData] = None
        self._is_logged: bool = False
        self._rooms: List[Room] = []
        self.server: Server = Server.WARSAW

    async def logout(self) -> None:
        if not self._is_logged:
            raise BotNotLoggedInError()
        self._is_logged = False
        await self.dispatch(BotEventHandler.on_logout, self)
        disconnect_tasks = []
        for room in list(self._rooms):
            disconnect_tasks.append(room.disconnect())
        await asyncio.gather(*disconnect_tasks)
        await self._bonk_api.close()
        self._bonk_api = None
        self._data = None
        self._rooms = []

    def add_room(self, room: 'Room') -> None:
        self._rooms.append(room)

    def remove_room(self, room: 'Room') -> None:
        self._rooms.remove(room)

    @property
    def event_loop(self) -> asyncio.AbstractEventLoop:
        return self._event_loop

    @property
    def is_logged(self) -> bool:
        return self._is_logged

    @property
    def rooms(self) -> List['Room']:
        return self._rooms.copy()

    @property
    def data(self) -> 'BotData':
        if self._data is None:
            raise BotNotLoggedInError()
        return self._data # TODO: Maybe better return a copy?

    @property
    def name(self) -> str:
        return self.data.name

    @property
    def xp(self) -> int:
        return self.data.xp

    @property
    def level(self) -> float:
        return xp_to_level(self.data.xp)

    @property
    def id(self) -> int:
        return self.data.id

    @property
    def is_guest(self) -> int:
        return self.data.is_guest

    @property
    def active_avatar_id(self) -> int:
        return self.data.active_avatar

    @active_avatar_id.setter
    def active_avatar_id(self, new_active_avatar_id: int) -> None:
        self.data.active_avatar = new_active_avatar_id

    @property
    def active_avatar(self) -> Avatar:
        return self.data.avatar

    @active_avatar.setter
    def active_avatar(self, new_avatar: 'Avatar') -> None:
        self.data.avatar = new_avatar

    def get_avatar(self, index: int) -> 'Avatar':
        return self.data.avatars[index]

    def set_avatar(self, index: int, avatar: 'Avatar') -> None:
        self.data.avatars[index] = avatar

    @property
    def friends(self) -> List[Friend]:
        return self.data.friends

    @property
    def legacy_friends(self) -> List[Friend]:
        return self.data.legacy_friends

    @property
    def settings(self) -> Settings:
        return self.data.settings

    @property
    def token(self) -> str:
        return self.data.token

    # region Sugar
    async def wait_for_connections(self) -> None:
        if not self._rooms:
            return
        await asyncio.gather(*[room.wait_for_connection() for room in self._rooms])
    # endregion

    # region API
    @property
    def aiohttp_session(self) -> aiohttp.ClientSession:
        return self._bonk_api.aiohttp_session

    @property
    def api_client(self) -> 'BonkAPI':
        return self._bonk_api
    # endregion

    async def __start(self, data: BotData) -> None:
        self._data = data
        self._is_logged = True
        await self.dispatch(BotEventHandler.on_ready, self)

    async def login_as_guest(self, name: str) -> None:
        if self._is_logged:
            raise ValueError('BonkBot already logged in')
        validate_username(name)
        await self.__start(BotData(name=name))

    async def login_with_password(self, name: str, password: str, *, remember: bool = False) -> Union[str, None]:
        if self._is_logged:
            raise ValueError('BonkBot already logged in')
        result = await self.api_client.fetch_data_with_password(name, password, remember=remember)
        if isinstance(result, ErrorType):
            raise ApiError(result)
        await self.__start(result)
        result: BotData
        return result.remember_token

    async def login_with_token(self, remember_token: str) -> None:
        if self._is_logged:
            raise ValueError('BonkBot already logged in')
        result = await self.api_client.fetch_data_with_token(remember_token)
        if isinstance(result, ErrorType):
            raise ApiError(result)
        await self.__start(result)

    def create_room(self, name: str = '', password: str = '', *, unlisted: bool = False,
                    max_players: int = 6, min_level: int = 0, max_level: int = 999, server: 'Server' = None) -> 'Room':
        if server is None:
            server = self.server
        room = Room(bot=self, room_params=RoomCreateParams(
            name=name,
            password=password,
            unlisted=unlisted,
            max_players=max_players,
            min_level=min_level,
            max_level=max_level,
            server=server,
        ))
        return room

    async def join_room(self, room_id: int, password: Optional[str] = None, bypass: Optional[str] = None) -> Optional['Room']:
        result = await self.api_client.fetch_room_data(room_id, password, bypass)
        if isinstance(result, ErrorType):
            raise ApiError(result)
        result: RoomJoinParams
        return Room(bot=self, room_params=result)

    async def join_room_via_link(self, link: str, password: str = '') -> Optional['Room']:
        result = await self.api_client.fetch_room_data_via_link(link, password)
        if isinstance(result, ErrorType):
            raise ApiError(result)
        result: RoomJoinParams
        return Room(bot=self, room_params=result)

    async def update_server(self) -> 'Server':
        server = await self.api_client.fetch_server()
        self.server = server
        return server

    async def fetch_rooms(self) -> List[RoomInfo]:
        return await self.api_client.fetch_rooms()

    async def wait_for_connection(self) -> None:
        await asyncio.gather(*[room.wait_for_connection() for room in self.rooms])

    def update_xp(self, new_xp: int) -> None:
        self.data.xp = new_xp

    def update_token(self, new_token: str) -> None:
        self.data.token = new_token

    async def fetch_friends(self) -> List['Friend']:
        return await self.api_client.fetch_friends(self.token)

    async def fetch_own_maps(self, start_from: int) -> List['BonkMap']:
        return await self.api_client.fetch_own_maps(self.token, start_from)

    # TODO: Get favs, b2, b1, map delete
