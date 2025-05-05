import asyncio
from typing import List, Union

import aiohttp

from bonkbot.core import PROTOCOL_VERSION, get_rooms_api, login_legacy_api
from bonkbot.core.bot_data import BotData
from bonkbot.core.bot_event_handler import BotEventHandler
from bonkbot.pson import ByteBuffer
from bonkbot.types import Mode
from bonkbot.types.avatar.avatar import Avatar
from bonkbot.types.errors.api_error import ApiError
from bonkbot.types.friend import Friend
from bonkbot.types.room_info import RoomInfo
from bonkbot.types.settings import Settings
from bonkbot.utils import validate_username, xp_to_level


class BonkBot(BotEventHandler):
    _data: Union[BotData, None]
    _aiohttp_session: Union[aiohttp.ClientSession, None]
    _is_logged: bool
    event_loop: asyncio.AbstractEventLoop

    def __init__(self):
        super().__init__()
        self._data = None
        self._is_logged = False
        self.event_loop = asyncio.get_event_loop()
        self._aiohttp_session = aiohttp.ClientSession(loop=self.event_loop)

    def __del__(self):
        self.event_loop.run_until_complete(self._aiohttp_session.close())

    @property
    def is_logged(self) -> bool:
        return self._is_logged

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
    def dbid(self) -> int:
        return self._data.dbid

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
        await self.event_emitter.emit_async('on_ready')

    def login_as_guest(self, name: str) -> None:
        if self._is_logged:
            raise ValueError('BonkBot already logged in')
        async def login():
            validate_username(name)
            data = BotData(
                name=name,
                token='',
                dbid=None,
                xp=None,
                avatar=Avatar(),
                active_avatar=0,
                avatars=[Avatar() for _ in range(5)],
                friends=[],
                legacy_friends=[],
                settings=Settings(),
            )
            await self._start(data)
        self.event_loop.run_until_complete(login())
    
    def login_with_password(self, name: str, password: str, *, remember: bool = False) -> Union[str, None]:
        if self._is_logged:
            raise ValueError('BonkBot already logged in')
        async def login():
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
                await self.event_emitter.emit_async('on_error', ApiError(response_data['e']))
                return
            await self._start(BotData.from_login_response(response_data))
            return response_data['rememberToken']
        return self.event_loop.run_until_complete(login())

    def login_with_token(self, remember_token: str) -> None:
        if self._is_logged:
            raise ValueError('BonkBot already logged in')
        async def login():
            response = await self._aiohttp_session.post(
                login_legacy_api,
                data={
                    'rememberToken': remember_token,
                }
            )
            response.raise_for_status()
            response_data = await response.json()
            if response_data['r'] == 'fail':
                await self.event_emitter.emit_async('on_error', ApiError(response_data['e']))
                return
            await self._start(BotData.from_login_response(response_data))
        return self.event_loop.run_until_complete(login())

    async def fetch_rooms(self) -> List[RoomInfo]:
        response = await self._aiohttp_session.post(
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
                dbid=room['id'],
                players=room['players'],
                max_players=room['maxplayers'],
                has_password=room['password'] == 1,
                mode=Mode.from_mode_code(room['mode_mo']),
                min_level=room['minlevel'],
                max_level=room['maxlevel'],
            ) for room in response_data['rooms']
        ]
