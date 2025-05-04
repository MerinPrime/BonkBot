import asyncio
from typing import List, Union

import aiohttp

from bonkbot.core.api import login_legacy_api
from bonkbot.core.bot_data import BotData
from bonkbot.core.bot_event_handler import BotEventHandler
from bonkbot.pson import ByteBuffer
from bonkbot.types.avatar.avatar import Avatar
from bonkbot.types.errors.login_error import LoginError
from bonkbot.types.friend import Friend
from bonkbot.types.settings import Settings
from bonkbot.utils import validate_username, xp_to_level


class BonkBot(BotEventHandler):
    _data: Union[BotData, None]
    aiohttp_session: Union[aiohttp.ClientSession, None]
    is_logged: bool

    def __init__(self):
        super().__init__()
        self._data = None
        self.aiohttp_session = None
        self.is_logged = False
        self.event_loop = asyncio.get_event_loop()
        self.aiohttp_session = aiohttp.ClientSession(loop=self.event_loop)

    def __del__(self):
        self.event_loop.run_until_complete(self.aiohttp_session.close())

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
    
    async def _start(self, data: BotData) -> None:
        self._data = data
        self.is_logged = True
        await self.event_emitter.emit_async('on_ready')

    def login_as_guest(self, name: str) -> None:
        if self.is_logged:
            raise ValueError('BonkBot already logged in')
        async def login():
            validate_username(name)
            data = BotData(
                name=name,
                token=None,
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

    async def login_by_data(self, json_data: dict) -> None:
        if self.is_logged:
            raise ValueError('BonkBot already logged in')
        data = BotData()
        data.name = json_data['username']
        data.token = json_data['token']
        data.dbid = json_data['id']
        data.xp = json_data['xp']
        data.avatar = Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar'], uri_encoded=True))
        data.active_avatar = json_data['activeAvatarNumber']
        data.avatars = [
            Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar1'], uri_encoded=True)),
            Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar2'], uri_encoded=True)),
            Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar3'], uri_encoded=True)),
            Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar4'], uri_encoded=True)),
            Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar5'], uri_encoded=True))
        ]
        data.friends = [Friend(
            name=friend['name'],
            dbid=friend['id'],
            room_id=friend['roomid']
        ) for friend in json_data['friends']]
        data.legacy_friends = [Friend(name=friend) for friend in json_data['legacyFriends'].split('#')]
        data.settings = Settings.from_buffer(ByteBuffer().from_base64(json_data['controls'], uri_encoded=False))
        await self._start(data)

    def login_with_password(self, name: str, password: str, *, remember: bool = False) -> Union[str, None]:
        if self.is_logged:
            raise ValueError('BonkBot already logged in')
        async def login():
            response = await self.aiohttp_session.post(
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
                await self.event_emitter.emit_async('on_error', LoginError(response_data['e']))
                return
            await self.login_by_data(response_data)
            return response_data['rememberToken']
        return self.event_loop.run_until_complete(login())

    def login_with_token(self, remember_token: str) -> None:
        if self.is_logged:
            raise ValueError('BonkBot already logged in')
        async def login():
            response = await self.aiohttp_session.post(
                login_legacy_api,
                data={
                    'rememberToken': remember_token,
                }
            )
            response.raise_for_status()
            response_data = await response.json()
            if response_data['r'] == 'fail':
                raise LoginError(response_data['e'])
            await self.login_by_data(response_data)
        return self.event_loop.run_until_complete(login())

