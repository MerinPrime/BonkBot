import dataclasses
from typing import TYPE_CHECKING, Dict, List, Union

import socketio
from peerjs.dataconnection import DataConnection
from peerjs.enums import PeerEventType
from peerjs.peer import Peer, PeerOptions

from ..types.mode import Mode
from ..types.room_info import RoomInfo
from ..types.server import Server
from .api import bonk_socket_api
from .timesyncer import TimeSyncer

if TYPE_CHECKING:
    from .bonkbot import BonkBot

# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/network/NetworkEngine.ts
class Room:
    _bot: "BonkBot"
    _room_info: "RoomInfo"
    _server: Server
    _create: bool
    _socket: socketio.AsyncClient
    _peer_ready: bool = False
    _time_offset: int = 0xFFFFFFFF
    _synced: bool = False
    _peer_id: str = ''
    _connections: List[DataConnection]
    _timesync_id: int = 0
    # _players: List[]

    def __init__(self, bot: "BonkBot", room_info: RoomInfo, *, create: bool, server: Server = Server.WARSAW) -> None:
        self._bot = bot
        self._room_info = dataclasses.replace(room_info)
        self._server = server
        self._create = create
        self._socket = socketio.AsyncClient(ssl_verify=True)

    @property
    def name(self) -> str:
        return self._room_info.name

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
    def mode(self) -> Mode:
        return self._room_info.mode

    @property
    def min_level(self) -> Union[int, None]:
        return self._room_info.min_level

    @property
    def max_level(self) -> Union[int, None]:
        return self._room_info.max_level

    @property
    def socket(self) -> socketio.AsyncClient:
        return self._socket

    @property
    def server(self) -> Server:
        return self._server

    async def connect(self) -> None:
        await self._bind_listeners()
        await self._socket.connect(bonk_socket_api.format(self._server.name))
        await self._make_timesync()
        await self._make_peer()

    async def _init_connection(self):
        print('INIT')

    async def _make_timesync(self):
        self.timesyncer = TimeSyncer(10, 1, 0.25, 5, self._socket)

        @self.timesyncer.event_emitter.on('sync')
        async def on_sync(state: str):
            if state == 'end' and not self._synced:
                self._synced = True
                if self._peer_ready:
                    await self._init_connection()

        @self.timesyncer.event_emitter.on('change')
        async def on_change(offset: int):
            if self._time_offset != 0xFFFFFFFF:
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
            self._connections.append(connection)
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

    async def _bind_listeners(self):
        pass

