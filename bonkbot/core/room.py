import asyncio
import dataclasses
import time
from typing import TYPE_CHECKING, Dict, Union

import socketio
from peerjs.dataconnection import DataConnection
from peerjs.enums import PeerEventType
from peerjs.peer import Peer, PeerOptions

from ..types.errors.room_already_connected import RoomAlreadyConnected
from ..types.room.room_action import RoomAction
from ..types.room.room_create_params import RoomCreateParams
from ..types.room.room_info import RoomInfo
from ..types.room.room_join_params import RoomJoinParams
from ..types.server import Server
from . import PROTOCOL_VERSION
from .api import bonk_socket_api
from .timesyncer import TimeSyncer

if TYPE_CHECKING:
    from ..types.mode import Mode
    from .bonkbot import BonkBot

# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/network/NetworkEngine.ts
class Room:
    _bot: "BonkBot"
    _room_params: Union["RoomJoinParams", "RoomCreateParams"]
    _room_info: "RoomInfo"
    _server: Server
    _action: RoomAction
    _socket: socketio.AsyncClient
    _peer_ready: bool
    _time_offset: int
    _synced: bool
    _peer_id: str
    _is_connected: bool
    # _players: List[]

    def __init__(self, bot: "BonkBot", room_params: Union["RoomJoinParams", "RoomCreateParams"],
                 *, server: Server = Server.WARSAW) -> None:
        self._bot = bot
        self._room_params = dataclasses.replace(room_params)
        self._room_info = None
        self._server = server
        self._action = RoomAction.CREATE if isinstance(room_params, RoomCreateParams) else RoomAction.JOIN
        self._socket = socketio.AsyncClient(ssl_verify=False)
        self._peer_ready = False
        self._time_offset = None
        self._synced = False
        self._peer_id = None
        self._is_connected = False
        self._bot.add_room(self)

    def __del__(self):
        if self._bot.event_loop.is_running():
            self._bot.event_loop.run_until_complete(self.disconnect())

    async def disconnect(self):
        if self.is_connected:
            await self._socket.disconnect()
        if self.peer_ready:
            await self._peer.destroy()
        self._room_info = None
        self._peer_ready = False
        self._time_offset = None
        self._synced = False
        self._peer_id = None
        self._is_connected = False
        self._bot.remove_room(self)

    @property
    def name(self) -> str:
        return self._room_info.name

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def peer_ready(self) -> bool:
        return self._peer_ready

    @property
    def dbid(self) -> int:
        return self._room_info.dbid

    @property
    def player_count(self) -> int:
        return self._room_info.players

    @property
    def has_password(self) -> bool:
        return self._room_info.has_password

    @property
    def mode(self) -> "Mode":
        return self._room_info.mode

    @property
    def min_level(self) -> Union[int, None]:
        return self._room_info.min_level

    @property
    def max_level(self) -> Union[int, None]:
        return self._room_info.max_level

    @property
    def password(self) -> Union[str, None]:
        return self._room_params.password

    @property
    def is_unlisted(self) -> Union[bool, None]:
        return self._room_params.unlisted

    @property
    def socket(self) -> socketio.AsyncClient:
        return self._socket

    @property
    def server(self) -> Server:
        return self._server

    async def connect(self) -> None:
        if self.is_connected:
            await self._bot.event_emitter.emit_async('on_error', RoomAlreadyConnected(self))
        self._bind_listeners()
        async def init_socket():
            await self._socket.connect(bonk_socket_api.format(self._server.name), transports=['websocket'])
            await self._make_timesync()
        await asyncio.gather(
            init_socket(),
            self._make_peer()
        )

    async def _init_connection(self):
        if self._action == RoomAction.CREATE:
            await self._create()
        else:
            await self._join()
        print('connected', time.time())

    async def _create(self) -> None:
        name = self._room_params.name
        if name is None:
            name = f'{self._bot.name}\'s game'
        data = {
            'peerID': self._peer_id,
            'roomName': name,
            'maxPlayers': self._room_params.max_players,
            'password': self._room_params.password,
            'dbid': self._bot.dbid,
            'guest': self._bot.is_guest,
            'minLevel': self._room_params.min_level,
            'maxLevel': self._room_params.max_level,
            'latitude': self.server.latitude,
            'longitude': self.server.longitude,
            'country': self.server.country,
            'version': PROTOCOL_VERSION,
            'hidden': int(self._room_params.unlisted),
            'quick': False,
            'mode': 'custom',
            'avatar': self._bot.active_avatar.to_json()
        }
        if self._bot.is_guest:
            data['guestName'] = self._bot.name
        else:
            data['token'] = self._bot.token
        await self._socket.emit(12, data)

    async def _join(self) -> None:
        pass

    async def _make_timesync(self):
        self.timesyncer = TimeSyncer(
            interval=10,
            timeout=1,
            delay=0.25,
            repeat=5,
            socket=self._socket
        )

        @self.timesyncer.event_emitter.on('sync')
        async def on_sync(state: str):
            if state == 'end' and not self._synced:
                self._synced = True
                if self.peer_ready:
                    await self._init_connection()

        @self.timesyncer.event_emitter.on('change')
        async def on_change(offset: int):
            if self._time_offset is not None:
                await self._bot.event_emitter.emit_async('time_offset_change', self, offset - self._time_offset)
            self._time_offset = offset

        await self.timesyncer.start()

    async def _make_peer(self):
        self._peer = Peer(peer_options=PeerOptions(
            host='b2warsaw1.bonk.io',
            port=443,
            path='/myapp',
            secure=True
        ))

        @self._peer.on(PeerEventType.Open)
        async def on_open(peer_id: str) -> None:
            self._peer_ready = True
            self._peer_id = peer_id
            if self._synced:
                await self._init_connection()

        @self._peer.on(PeerEventType.Connection)
        async def on_connection(connection: DataConnection) -> None:
            self._peer_ready = True
            # TODO: set data connection for player
            await self._process_new_connection(connection)

        @self._peer.on(PeerEventType.Error)
        async def on_error(error: str) -> None:
            # print(error)
            pass

        await self._peer.start()

    async def _process_new_connection(self, connection: DataConnection) -> None:
        @connection.on('data')
        async def on_data(data: Dict) -> None:
            print(data)

    def _bind_listeners(self):
        pass

