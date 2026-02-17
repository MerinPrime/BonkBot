import asyncio
from asyncio import AbstractEventLoop
from typing import TYPE_CHECKING, List, Optional

from aiohttp import ClientSession

from ...types.avatar.avatar import Avatar
from ...types.errors import BotAlreadyLoggedInError
from ...types.errors.api_error import ApiError
from ...types.errors.bot_not_logged_error import BotNotLoggedInError
from ...types.errors.error_type import ErrorType
from ...types.room.room_create_params import RoomCreateParams
from ...types.server import Server
from ...utils.api import validate_username
from ...utils.xp import xp_to_level
from ..room.room import Room
from .bonk_api import BonkAPI
from .bot_data import BotData
from .bot_event_handler import BotEventHandler

if TYPE_CHECKING:
    from ...types.friend import Friend
    from ...types.map import BonkMap
    from ...types.room.room_info import RoomInfo
    from ...types.settings import Settings


class BonkBot(BotEventHandler):
    def __init__(
        self,
        event_loop: Optional['AbstractEventLoop'] = None,
        aiohttp_session: Optional['ClientSession'] = None,
    ):
        super().__init__()
        if event_loop is None:
            event_loop = asyncio.get_event_loop()
        if aiohttp_session is None:
            aiohttp_session = ClientSession(loop=event_loop)
        self.server: Server = Server.WARSAW
        self._event_loop: AbstractEventLoop = event_loop
        self._bonk_api: BonkAPI = BonkAPI(event_loop, aiohttp_session)
        self._data: Optional[BotData] = None
        self._is_logged: bool = False
        self._rooms: List[Room] = []

    async def logout(self) -> None:
        if not self._is_logged:
            raise BotNotLoggedInError()
        await self.dispatch(BotEventHandler.on_logout, self)
        disconnect_tasks = []
        for room in list(self._rooms):
            disconnect_tasks.append(room.disconnect())
        await asyncio.gather(*disconnect_tasks)
        await self._bonk_api.close()
        self._bonk_api = None
        self._data = None
        self._is_logged = False
        self._rooms = []

    # region Sugar
    async def wait_for_connections(self) -> None:
        if not self._rooms:
            return
        await asyncio.gather(*[room.wait_for_connection() for room in self._rooms])

    # endregion

    async def __start(self, data: 'BotData') -> None:
        self._data = data
        self._is_logged = True
        await self.dispatch(BotEventHandler.on_ready, self)

    async def login_as_guest(self, name: str) -> None:
        if self._is_logged:
            raise BotAlreadyLoggedInError()
        error = validate_username(name, is_guest=True)
        if error is not None:
            raise ApiError(error)
        await self.__start(BotData(name=name))

    async def login_with_password(
        self,
        name: str,
        password: str,
        *,
        remember: bool = False,
        bypass_username_check: bool = False,
    ) -> Optional[str]:
        """
        Log in to an account using a username and password.

        :param name: Account name.
        :param password: Account password.
        :param remember: If True, return a remember token.
        :param bypass_username_check: Bypass username validation checks.
                                      Use this if you have legacy accounts with invalid username (e.g., empty name ).
        :return: Remember token if `remember` is True, else None.
        :raises BotAlreadyLoggedInError: If the bot is already logged in.
        :raises ApiError: If the API returns an error.
        """
        if self._is_logged:
            raise BotAlreadyLoggedInError()
        if not bypass_username_check:
            error = validate_username(name, is_guest=False)
            if error is not None:
                raise ApiError(error)
        result = await self._bonk_api.fetch_data_with_password(
            name,
            password,
            remember=remember,
        )
        if isinstance(result, ErrorType):
            raise ApiError(result)
        await self.__start(result)
        return result.remember_token

    async def login_with_token(self, remember_token: str) -> None:
        if self._is_logged:
            raise BotAlreadyLoggedInError()
        result = await self._bonk_api.fetch_data_with_token(remember_token)
        if isinstance(result, ErrorType):
            raise ApiError(result)
        await self.__start(result)

    def create_room(
        self,
        name: str = '',
        password: str = '',
        *,
        unlisted: bool = False,
        max_players: int = 6,
        min_level: int = 0,
        max_level: int = 999,
        server: 'Server' = None,
    ) -> 'Room':
        if not self._is_logged:
            raise BotNotLoggedInError()
        if name is None:
            name = f"{self.name}'s game"
        if not (1 <= max_players <= 8):
            raise ValueError('Max players must be between 1 and 8')
        if not (0 <= min_level <= max_level):
            raise ValueError('Min level must be between 0 and max_level')
        if not (0 <= max_level <= 999):
            raise ValueError('Max level must be between 0 and 999')
        if server is None:
            server = self.server
        room = Room(
            bot=self,
            room_params=RoomCreateParams(
                name=name,
                password=password,
                unlisted=unlisted,
                max_players=max_players,
                min_level=min_level,
                max_level=max_level,
                server=server,
            ),
        )
        return room

    async def join_room(
        self,
        room_id: int,
        password: Optional[str] = None,
        bypass: Optional[str] = None,
    ) -> Optional['Room']:
        if not self._is_logged:
            raise BotNotLoggedInError()
        result = await self.api_client.fetch_room_data(room_id, password, bypass)
        if isinstance(result, ErrorType):
            raise ApiError(result)
        return Room(bot=self, room_params=result)

    async def join_room_via_link(
        self,
        link: str,
        password: str = '',
    ) -> Optional['Room']:
        if not self._is_logged:
            raise BotNotLoggedInError()
        result = await self.api_client.fetch_room_data_via_link(link, password)
        if isinstance(result, ErrorType):
            raise ApiError(result)
        return Room(bot=self, room_params=result)

    def add_room(self, room: 'Room') -> None:
        self._rooms.append(room)

    def remove_room(self, room: 'Room') -> None:
        self._rooms.remove(room)

    def update_xp(self, new_xp: int) -> None:
        if not self._is_logged:
            raise BotNotLoggedInError()
        self._data.xp = new_xp

    def update_token(self, new_token: str) -> None:
        if not self._is_logged:
            raise BotNotLoggedInError()
        self._data.token = new_token

    async def update_server(self) -> 'Server':
        self.server = await self.fetch_server()
        return self.server

    async def fetch_server(self) -> 'Server':
        return await self._bonk_api.fetch_server()

    async def fetch_rooms(self) -> List['RoomInfo']:
        return await self._bonk_api.fetch_rooms()

    async def fetch_friends(self) -> List['Friend']:
        if not self._is_logged:
            raise BotNotLoggedInError()
        return await self._bonk_api.fetch_friends(self._data.token)

    async def fetch_own_maps(self, start_from: int) -> List['BonkMap']:
        if not self._is_logged:
            raise BotNotLoggedInError()
        return await self._bonk_api.fetch_own_maps(self._data.token, start_from)

    # TODO: Get favs, b2, b1, map delete

    @property
    def event_loop(self) -> 'AbstractEventLoop':
        return self._event_loop

    @property
    def api_client(self) -> 'BonkAPI':
        return self._bonk_api

    @property
    def aiohttp_session(self) -> 'ClientSession':
        return self._bonk_api.aiohttp_session

    @property
    def is_logged(self) -> bool:
        return self._is_logged

    @property
    def rooms(self) -> List['Room']:
        return self._rooms.copy()

    @property
    def data(self) -> 'BotData':
        if not self._is_logged:
            raise BotNotLoggedInError()
        return self._data  # TODO: Maybe better return a copy?

    @property
    def name(self) -> str:
        if not self._is_logged:
            raise BotNotLoggedInError()
        return self._data.name

    @property
    def xp(self) -> int:
        if not self._is_logged:
            raise BotNotLoggedInError()
        return self._data.xp

    @property
    def level(self) -> float:
        if not self._is_logged:
            raise BotNotLoggedInError()
        return xp_to_level(self._data.xp)

    @property
    def id(self) -> int:
        if not self._is_logged:
            raise BotNotLoggedInError()
        return self._data.id

    @property
    def is_guest(self) -> int:
        if not self._is_logged:
            raise BotNotLoggedInError()
        return self._data.is_guest

    @property
    def active_avatar_id(self) -> int:
        if not self._is_logged:
            raise BotNotLoggedInError()
        return self._data.active_avatar_id

    @active_avatar_id.setter
    def active_avatar_id(self, new_active_avatar_id: int) -> None:
        if not self._is_logged:
            raise BotNotLoggedInError()
        self._data.active_avatar_id = new_active_avatar_id

    @property
    def active_avatar(self) -> Avatar:
        if not self._is_logged:
            raise BotNotLoggedInError()
        return self._data.active_avatar

    @active_avatar.setter
    def active_avatar(self, new_avatar: 'Avatar') -> None:
        if not self._is_logged:
            raise BotNotLoggedInError()
        self._data.active_avatar = new_avatar

    def get_avatar(self, index: int) -> 'Avatar':
        if not self._is_logged:
            raise BotNotLoggedInError()
        return self._data.avatars[index]

    def set_avatar(self, index: int, avatar: 'Avatar') -> None:
        if not self._is_logged:
            raise BotNotLoggedInError()
        self._data.avatars[index] = avatar

    @property
    def friends(self) -> List['Friend']:
        if not self._is_logged:
            raise BotNotLoggedInError()
        return self._data.friends

    @property
    def legacy_friends(self) -> List['Friend']:
        if not self._is_logged:
            raise BotNotLoggedInError()
        return self._data.bonk_v1_friends

    @property
    def settings(self) -> 'Settings':
        if not self._is_logged:
            raise BotNotLoggedInError()
        return self._data.settings

    @property
    def token(self) -> str:
        if not self._is_logged:
            raise BotNotLoggedInError()
        return self._data.token

    @property
    def remember_token(self) -> str:
        if not self._is_logged:
            raise BotNotLoggedInError()
        return self._data.remember_token
