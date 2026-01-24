import asyncio
import re
from asyncio import AbstractEventLoop
from typing import List, Optional, Union

from aiohttp import ClientSession

from ..api.socket_events import PROTOCOL_VERSION

from ...types.server import Server
from ...types.mode import Mode
from ...types.friend import Friend
from ...types.errors.error_type import ErrorType
from ...types.map import BonkMap
from ...types.room import RoomInfo
from ...types.room.room_join_params import RoomJoinParams
from ..api.endpoints import (
    auto_join_api,
    get_friends_api,
    get_own_maps_api,
    get_room_address_api,
    get_rooms_api,
    login_legacy_api,
)
from .bot_data import BotData


class BonkAPI:
    def __init__(self, event_loop: Optional['AbstractEventLoop'] = None,
                 aiohttp_session: Optional['ClientSession'] = None) -> None:
        if event_loop is None:
            event_loop = asyncio.get_event_loop()
        if aiohttp_session is None:
            aiohttp_session = ClientSession(loop=event_loop)
        self._event_loop: AbstractEventLoop = event_loop
        self._aiohttp_session: ClientSession = aiohttp_session

    @property
    def event_loop(self) -> 'AbstractEventLoop':
        return self._event_loop

    @property
    def aiohttp_session(self) -> 'ClientSession':
        return self._aiohttp_session

    async def close(self) -> None:
        await self._aiohttp_session.close()

    async def fetch_data_with_password(self, name: str, password: str, *, remember: bool = False,
                                       ) -> Union['ErrorType', 'BotData']:
        response = await self._aiohttp_session.post(
            login_legacy_api,
            data={
                'username': name,
                'password': password,
                'remember': 'true' if remember else 'false',
            },
        )
        response.raise_for_status()
        response_data = await response.json()
        if response_data['r'] == 'fail':
            return ErrorType.from_string(response_data['e'])
        return BotData.from_login_response(response_data)

    async def fetch_data_with_token(self, remember_token: str) -> Union['ErrorType', 'BotData']:
        response = await self._aiohttp_session.post(
            login_legacy_api,
            data={
                'rememberToken': remember_token,
            },
        )
        response.raise_for_status()
        response_data = await response.json()
        if response_data['r'] == 'fail':
            return ErrorType.from_string(response_data['e'])
        return BotData.from_login_response(response_data)

    async def fetch_room_data(self, room_id: int, password: str = '', bypass: str = '',
                              ) -> Union['ErrorType', 'RoomJoinParams']:
        response = await self.aiohttp_session.post(
            url=get_room_address_api,
            data={
                'id': room_id,
            },
        )
        response.raise_for_status()
        response_data = await response.json()
        if response_data['r'] == 'fail':
            return ErrorType.from_string(response_data['e'])
        return RoomJoinParams(
            room_address=room_id,
            password=password,
            bypass=bypass,
            name=response_data['roomname'],
            server=Server.from_name(response_data['server']),
        )

    async def fetch_room_data_via_link(self, link: str, password: str = '',
                                       ) -> Union['ErrorType', 'RoomJoinParams']:
        regex = r'/(\d{6})([a-zA-Z0-9]{5})?$'
        match = re.search(regex, link)
        room_id = match.group(1)
        bypass = match.group(2)
        response = await self.aiohttp_session.post(url=auto_join_api, data={'joinID': room_id})
        response.raise_for_status()
        response_data = await response.json()
        if response_data['r'] == 'failed':
            return ErrorType.ROOM_NOT_FOUND
        return RoomJoinParams(
            room_address=response_data['address'],
            password=password,
            bypass=bypass,
            name=response_data['roomname'],
            server=Server.from_name(response_data['server']),
        )

    async def fetch_server(self) -> 'Server':
        response = await self.aiohttp_session.post(
            get_rooms_api,
            data={
                'version': PROTOCOL_VERSION,
                'gl': 'y',
                'token': '',
            },
        )
        response.raise_for_status()
        response_data = await response.json()
        return Server.from_name(response_data['createserver'])

    async def fetch_rooms(self) -> List['RoomInfo']:
        response = await self.aiohttp_session.post(
            get_rooms_api,
            data={
                'version': PROTOCOL_VERSION,
                'gl': 'n',
                'token': '',
            },
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

    async def fetch_friends(self, token: str) -> List['Friend']:
        response = await self.aiohttp_session.post(
            url=get_friends_api,
            data={
                'token': token,
                'task': 'getfriends',
            },
        )
        response.raise_for_status()
        response_data = await response.json()

        return [Friend(
            name=friend['name'],
            dbid=friend['id'],
            room_id=friend['roomid'],
        ) for friend in response_data['friends']]

    async def fetch_own_maps(self, token: str, start_from: int) -> List['BonkMap']:
        # Api returning maps from `start_from` to `start_from + 30`
        # Only 30 maps from `start_from` will be returned
        response = await self.aiohttp_session.post(
            url=get_own_maps_api,
            data={
                'token': token,
                'startingfrom': str(start_from),
            },
        )
        response.raise_for_status()
        response_data = await response.json()

        return [BonkMap.decode_from_database(bonk_map['leveldata']) for bonk_map in response_data['maps']]
