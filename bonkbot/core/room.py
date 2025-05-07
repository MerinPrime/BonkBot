import asyncio
import dataclasses
import random
import string
import time
from typing import TYPE_CHECKING, Dict, Union, List

import socketio
from peerjs_py import PeerEventType, PeerOptions, Peer
from peerjs_py.dataconnection.DataConnection import DataConnection

from ..types.avatar import Avatar
from ..types.errors.room_already_connected import RoomAlreadyConnected
from ..types.room.room_action import RoomAction
from ..types.room.room_create_params import RoomCreateParams
from ..types.room.room_join_params import RoomJoinParams
from ..types.room_data import RoomData
from ..types.server import Server
from . import PROTOCOL_VERSION
from .api import bonk_socket_api, room_link_api
from .timesyncer import TimeSyncer
from ..core.player import Player
from ..types.mode import Mode
from ..types.team import TeamState, Team

if TYPE_CHECKING:
    from .bonkbot import BonkBot

# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/network/NetworkEngine.ts
class Room:
    _bot: "BonkBot"
    _room_params: Union["RoomJoinParams", "RoomCreateParams"]
    _room_data: "RoomData"
    _total_players: int
    _server: Server
    _action: RoomAction
    _socket: socketio.AsyncClient
    _peer_ready: bool
    _time_offset: int
    _synced: bool
    _peer_id: str
    _is_connected: bool
    _players: List["Player"]
    _bot_player: "Player"

    def __init__(self, bot: "BonkBot", room_params: Union["RoomJoinParams", "RoomCreateParams"],
                 *, server: Server = Server.WARSAW) -> None:
        self._bot = bot
        self._room_params = dataclasses.replace(room_params)
        self._room_data = None
        self._server = server
        self._total_players = 0
        self._action = RoomAction.CREATE if isinstance(room_params, RoomCreateParams) else RoomAction.JOIN
        self._socket = socketio.AsyncClient(ssl_verify=False)
        self._peer_ready = False
        self._time_offset = None
        self._synced = False
        self._peer_id = None
        self._is_connected = False
        self._players = []
        self._bot_player = None
        self._bot.add_room(self)

    def __del__(self):
        if self._bot.event_loop.is_running():
            self._bot.event_loop.run_until_complete(self.disconnect())

    async def disconnect(self):
        if self.is_connected:
            await self._socket.disconnect()
        if self.peer_ready:
            await self._peer.destroy()
        self._room_data = None
        self._peer_ready = False
        self._time_offset = None
        self._synced = False
        self._peer_id = None
        self._is_connected = False
        self._bot.remove_room(self)

    @property
    def name(self) -> str:
        return self._room_data.name

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def peer_ready(self) -> bool:
        return self._peer_ready

    @property
    def id(self) -> int:
        return self._room_data.id

    @property
    def player_count(self) -> int:
        return len(self._room_data.players)
    
    @property
    def players(self) -> List["Player"]:
        return self._room_data.players

    @property
    def has_password(self) -> bool:
        return self._room_data.password is not None

    @property
    def mode(self) -> "Mode":
        return self._room_data.mode

    @property
    def min_level(self) -> Union[int, None]:
        return self._room_params.min_level

    @property
    def max_level(self) -> Union[int, None]:
        return self._room_params.max_level

    @property
    def password(self) -> Union[str, None]:
        return self._room_data.password

    @property
    def host(self) -> "Player":
        return self._room_data.host

    @property
    def rounds(self) -> int:
        return self._room_data.rounds

    @property
    def team_state(self) -> "TeamState":
        return self._room_data.team_state

    @property
    def team_lock(self) -> bool:
        return self._room_data.team_lock

    @property
    def is_unlisted(self) -> Union[bool, None]:
        return self._room_params.unlisted

    @property
    def socket(self) -> socketio.AsyncClient:
        return self._socket

    @property
    def server(self) -> "Server":
        return self._server

    @property
    def join_id(self) -> str:
        return self._room_data.join_id

    @property
    def join_bypass(self) -> str:
        return self._room_data.join_bypass

    @property
    def join_link(self) -> str:
        if self._room_data.join_id is None:
            return ''
        return room_link_api.format(self.join_id, self.join_bypass)

    @property
    def bot(self) -> "Player":
        return self._bot_player

    async def connect(self) -> None:
        if self.is_connected:
            await self._bot.dispatch('on_error', RoomAlreadyConnected(self))
        self._bind_listeners()
        async def init_socket():
            await self._socket.connect(bonk_socket_api.format(self._server.name), transports=['websocket'])
            await self._make_timesync()
        await asyncio.gather(
            init_socket(),
            self._make_peer()
        )

    async def _init_connection(self):
        print('beb')
        if self._action == RoomAction.CREATE:
            await self._create()
        else:
            await self._join()

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
        self._bot_player = Player(
            bot=self._bot,
            room=self,
            data_connection=None,
            id=0,
            team=Team.FFA,
            avatar=self._bot.active_avatar,
            name=self._bot.name,
            is_guest=self._bot.is_guest,
            ready=False,
            tabbed=True,
            level=self._bot.level,
            peer_id=self._peer_id,
            joined_with_bypass=None,
        )
        self._room_data = RoomData(
            name=name,
            host=self._bot_player,
            players=[self._bot_player]
        )
        self._total_players = 1
        print(123)
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
                await self._bot.dispatch('time_offset_change', self, offset - self._time_offset)
            self._time_offset = offset

        await self.timesyncer.start()

    async def _make_peer(self):
        print('123')
        response = await self._bot.aiohttp_session.get('https://b2warsaw1.bonk.io/myapp/peerjs/id')
        peer_id = await response.text()
        self._peer = Peer(id=peer_id, options=PeerOptions(
            host='{}.bonk.io'.format(self._server.name),
            port=443,
            path='/myapp',
            secure=True
        ))

        @self._peer.on(PeerEventType.Open.value)
        async def on_open(peer_id: str) -> None:
            self._peer_ready = True
            self._peer_id = peer_id
            if self._synced:
                await self._init_connection()

        @self._peer.on(PeerEventType.Connection.value)
        async def on_connection(connection: DataConnection) -> None:
            self._peer_ready = True
            # TODO: set data connection for player

        @self._peer.on(PeerEventType.Error.value)
        async def on_error(error: str) -> None:
            pass

        await self._peer.start()
        # TODO: fix peers or end fork of peerjs-python

    async def _process_new_connection(self, connection: DataConnection) -> None:
        async def on_data(data: Dict) -> None:
            print(data,time.time())
        
        connection.data_channel.on('message', lambda data: asyncio.create_task(on_data(data)))

    async def _init_player_peer(self, player: Player):
        player.data_connection = await self._peer.connect(player.peer_id)
        print(player.data_connection)
        await self._process_new_connection(player.data_connection)
    
    def _bind_listeners(self):
        @self.socket.on(1)
        async def on_ping_data(pings: Dict, player_id: int):
            await self.socket.emit(1, {'id': player_id})
            for player_id, ping in pings.items():
                self._room_data.players[int(player_id)].ping = ping
            await self._bot.dispatch('on_ping_data', self)
        
        @self.socket.on(2)
        async def on_room_create(*args):
            await self._bot.dispatch('on_room_connection', self, RoomAction.CREATE)
        
        @self.socket.on(3)
        async def on_room_join(bot_id: int, host_id: int, players: Dict, timestamp: int, team_lock: bool,
                                 join_id: int, join_bypass: str, *args):
            self._room_data.join_id = f'{join_id:06}'
            self._room_data.join_bypass = join_bypass
            self._room_data.team_lock = team_lock
            self._room_data.host_id = host_id
            self._total_players = len(players)
            for player_id, player_data in players.items():
                player = Player(
                    bot=self._bot,
                    room=self,
                    data_connection=None,
                    id=player_id,
                    team=Team.from_number(player_data['team']),
                    avatar=Avatar.from_json(player_data['avatar']),
                    peer_id=player_data['peerID'],
                    name=player_data['userName'],
                    is_guest=player_data['is_guest'],
                    ready=player_data['ready'],
                    tabbed=player_data['tabbed'],
                    level=player_data['level'],
                    joined_with_bypass=None,
                )
                if player_id == bot_id:
                    self._bot_player = player
                else:
                    self._bot.event_loop.create_task(self._init_player_peer(player))
                self._room_data.players.append(player)
            self._bot_player = self._room_data.player_by_id(bot_id)
            self._room_data.host = self._room_data.player_by_id(host_id)
            await self._bot.dispatch('on_room_connection', self, RoomAction.JOIN)

        @self.socket.on(4)
        async def on_player_join(player_id: int, peer_id: str, username: str, is_guest: bool, level: int,
                joined_with_bypass: int, avatar: Dict):
            player = Player(
                bot=self._bot,
                room=self,
                data_connection=None,
                id=player_id,
                team=Team.FFA if self.team_state == TeamState.FFA and self.team_lock == False else Team.SPECTATOR,
                avatar=Avatar.from_json(avatar),
                peer_id=peer_id,
                name=username,
                is_guest=is_guest,
                ready=False,
                tabbed=True,
                level=level,
                joined_with_bypass=joined_with_bypass,
            )
            print('join')
            asyncio.create_task(self._init_player_peer(player))
            self._room_data.players.append(player)
            await self._bot.dispatch('on_player_join', self, player)
            bad_map_data = {
                "v": 13,
                "s": {
                    "re": False,
                    "nc": False,
                    "pq": 1,
                    "gd": 25,
                    "fl": False
                },
                "physics": {
                    "shapes": [],
                    "fixtures": [],
                    "bodies": [],
                    "bro": [],
                    "joints": [],
                    "ppm": 12
                },
                "spawns": [],
                "capZones": [],
                "m": {
                    "a": 'kalalak',
                    "n": 'kalalak',
                    "dbv": 2,
                    "dbid": -1,
                    "authid": -1,
                    "date": '',
                    "rxid": 0,
                    "rxn": "",
                    "rxa": "",
                    "rxdb": 1,
                    "cr": [
                        "💀"
                    ],
                    "pub": True,
                    "mo": "",
                    "vu": 5,
                    "vd": 5
                }
            }
            await self._socket.emit(
                11,
                {
                    "sid": player_id,
                    "gs": {
                        "map": bad_map_data,
                        "gt": 2,
                        "wl": self.rounds,
                        "q": False,
                        "tl": self.team_lock,
                        "tea": self.team_state != TeamState.FFA,
                        "ga": self.mode.engine,
                        "mo": self.mode.mode,
                        "bal": []
                    }
                })
            await asyncio.sleep(5)
            await self._socket.emit(34, {'id': 1})

        @self.socket.on(49)
        async def on_room_id_obtain(join_id: int, join_bypass: str):
            self._room_data.join_id = f'{join_id:06}'
            self._room_data.join_bypass = join_bypass
            print(self.join_link)
            await self._bot.dispatch('on_room_id_obtain', self)
        

