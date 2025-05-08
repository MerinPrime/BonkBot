import asyncio
from typing import List, Optional, Union

import aiohttp

from ..types import Server
from ..types.avatar.avatar import Avatar
from ..types.errors import ApiError, ErrorType
from ..types.friend import Friend
from ..types.mode import Mode
from ..types.room.room_create_params import RoomCreateParams
from ..types.room.room_info import RoomInfo
from ..types.room.room_join_params import RoomJoinParams
from ..types.settings import Settings
from ..utils.api import validate_username
from ..utils.xp import xp_to_level
from .api import PROTOCOL_VERSION, get_rooms_api, login_legacy_api
from .bot_data import BotData
from .bot_event_handler import BotEventHandler
from .room import Room


class BonkBot(BotEventHandler):
    _data: Union[BotData, None]
    _aiohttp_session: Union[aiohttp.ClientSession, None]
    _is_logged: bool
    _event_loop: asyncio.AbstractEventLoop
    _rooms: List[Room]
    server: Server

    def __init__(self, event_loop: Optional[asyncio.AbstractEventLoop] = None):
        super().__init__()
        self._data = None
        self._is_logged = False
        self._event_loop = event_loop if event_loop is not None else asyncio.get_event_loop()
        self._aiohttp_session = aiohttp.ClientSession(loop=self.event_loop)
        self._rooms = []
        self.server = Server.WARSAW

    async def logout(self) -> None:
        await self.dispatch('on_logout', self)
        self._is_logged = False
        if not self.aiohttp_session.closed:
            await self.aiohttp_session.close()
        for room in self._rooms:
            await room.disconnect()
        self._data = None
        self._event_loop = None
        self._aiohttp_session = None
        self._rooms = []
        self.server = Server.WARSAW

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
    def aiohttp_session(self) -> aiohttp.ClientSession:
        return self._aiohttp_session

    @property
    def name(self) -> str:
        return self._data.name

    @property
    def xp(self) -> int:
        return self._data.xp

    @property
    def level(self) -> float:
        return xp_to_level(self._data.xp)

    @property
    def id(self) -> int:
        return self._data.id

    @property
    def is_guest(self) -> int:
        return self._data.is_guest

    @property
    def active_avatar_id(self) -> int:
        return self._data.active_avatar

    @active_avatar_id.setter
    def active_avatar_id(self, new_active_avatar_id: int) -> None:
        self._data.active_avatar = new_active_avatar_id

    @property
    def active_avatar(self) -> Avatar:
        return self._data.avatar

    @active_avatar.setter
    def active_avatar(self, new_avatar: Avatar) -> None:
        self._data.avatar = new_avatar

    def get_avatar(self, index: int) -> Avatar:
        return self._data.avatars[index]

    def set_avatar(self, index: int) -> Avatar:
        return self._data.avatars[index]

    @property
    def friends(self) -> List[Friend]:
        return self._data.friends

    @property
    def legacy_friends(self) -> List[Friend]:
        return self._data.legacy_friends

    @property
    def settings(self) -> Settings:
        return self._data.settings

    @property
    def token(self) -> str:
        return self._data.token

    async def _start(self, data: BotData) -> None:
        self._data = data
        self._is_logged = True
        await self.dispatch('on_ready', self)

    async def login_as_guest(self, name: str) -> None:
        if self._is_logged:
            raise ValueError('BonkBot already logged in')
        validate_username(name)
        data = BotData(
            name=name,
            token='',
            id=0,
            is_guest=True,
            xp=0,
            avatar=Avatar(),
            active_avatar=0,
            avatars=[Avatar() for _ in range(5)],
            friends=[],
            legacy_friends=[],
            settings=Settings(),
        )
        await self._start(data)

    async def login_with_password(self, name: str, password: str, *, remember: bool = False) -> Union[str, None]:
        if self._is_logged:
            raise ValueError('BonkBot already logged in')
        response = await self._aiohttp_session.post(
            login_legacy_api,
            data={
                'username': name,
                'password': password,
                'remember': 'true' if remember else 'false',
            }
        )
        response.raise_for_status()
        response_data = await response.json()
        if response_data['r'] == 'fail':
            await self.dispatch('on_error', self, ApiError(ErrorType.from_string(response_data['e'])))
            return
        await self._start(BotData.from_login_response(response_data))
        return response_data['rememberToken']

    async def login_with_token(self, remember_token: str) -> None:
        if self._is_logged:
            raise ValueError('BonkBot already logged in')
        response = await self._aiohttp_session.post(
            login_legacy_api,
            data={
                'rememberToken': remember_token,
            }
        )
        response.raise_for_status()
        response_data = await response.json()
        if response_data['r'] == 'fail':
            await self.dispatch('on_error', self, ApiError(ErrorType.from_string(response_data['e'])))
            return
        await self._start(BotData.from_login_response(response_data))

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
        ), server=server)
        return room

    def join_room(self, room_info: 'RoomInfo', password: str = '', bypass: str = '', *, server: Optional['Server'] = None) -> 'Room':
        if server is None:
            server = self.server
        room = Room(bot=self, room_params=RoomJoinParams(
            room_id=room_info.id,
            password=password,
            bypass=bypass,
        ), server=server)
        return room

    async def update_server(self) -> 'Server':
        response = await self.aiohttp_session.post(
            get_rooms_api,
            data={
                'version': PROTOCOL_VERSION,
                'gl': 'y',
                'token': self._data.token,
            }
        )
        response.raise_for_status()
        response_data = await response.json()
        server = Server.from_name(response_data['createserver'])
        self.server = server
        return server

    async def fetch_rooms(self) -> List[RoomInfo]:
        response = await self.aiohttp_session.post(
            get_rooms_api,
            data={
                'version': PROTOCOL_VERSION,
                'gl': 'n',
                'token': self._data.token,
            }
        )
        response.raise_for_status()
        response_data = await response.json()
        return [
            RoomInfo(
                name=room['roomname'],
                id=room['id'],
                players=room['players'],
                max_players=room['maxplayers'],
                has_password=room['password'] == 1,
                mode=Mode.from_mode_code(room['mode_mo']),
                min_level=room['minlevel'],
                max_level=room['maxlevel'],
            ) for room in response_data['rooms']
        ]

    async def wait_for_connection(self):
        await asyncio.gather(*[room.wait_for_connection() for room in self.rooms])
