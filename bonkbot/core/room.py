import asyncio
import copy
import dataclasses
import random
import string
import time
from typing import TYPE_CHECKING, Dict, List, Union

import socketio
from peerjs_py import Peer, PeerOptions
from peerjs_py.dataconnection.BufferedConnection.BinaryPack import BinaryPack
from peerjs_py.dataconnection.DataConnection import DataConnection

from ..core.player import Player
from ..pson import StaticPair, ByteBuffer
from ..types.avatar import Avatar
from ..types.errors import ApiError, ErrorType
from ..types.errors.room_already_connected import RoomAlreadyConnected
from ..types.map.bonkmap import BonkMap
from ..types.player_move import PlayerMove
from ..types.room.room_action import RoomAction
from ..types.room.room_create_params import RoomCreateParams
from ..types.room.room_data import RoomData
from ..types.server import Server
from ..types.team import Team, TeamState
from . import PROTOCOL_VERSION
from .api import (
    CRITICAL_API_ERRORS,
    RATE_LIMIT_PONG,
    SocketEvents,
    bonk_peer_api,
    bonk_socket_api,
    room_link_api, PSON_KEYS,
)
from .timesyncer import TimeSyncer

if TYPE_CHECKING:
    from ..types.mode import Mode
    from ..types.room.room_join_params import RoomJoinParams
    from .bonkbot import BonkBot

# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/network/NetworkEngine.ts
class Room:
    _bot: 'BonkBot'
    _room_params: Union['RoomJoinParams', 'RoomCreateParams']
    _room_data: 'RoomData'
    _total_players: int
    _server: Server
    _action: RoomAction
    _socket: socketio.AsyncClient
    _peer_ready: bool
    _time_offset: int
    _synced: bool
    _peer_id: str
    _is_connected: bool
    _bot_player: 'Player'
    _connect_event: asyncio.Event
    _map: BonkMap
    _connection: List['DataConnection']
    _p2p_revert_task: asyncio.Task

    def __init__(self, bot: 'BonkBot', room_params: Union['RoomJoinParams', 'RoomCreateParams'],
                 *, server: Server = Server.WARSAW) -> None:
        self._bot = bot
        self._room_params = dataclasses.replace(room_params)
        self._room_data = None
        self._server = server
        self._total_players = 0
        self._action = RoomAction.CREATE if isinstance(room_params, RoomCreateParams) else RoomAction.JOIN
        self._socket = socketio.AsyncClient(ssl_verify=False)
        self._bind_listeners()
        self._peer_ready = False
        self._time_offset = None
        self._synced = False
        self._peer_id = None
        self._is_connected = False
        self._bot_player = None
        self._p2p_revert_task = None
        self._connections = []
        self._connect_event = asyncio.Event()
        self._bot.add_room(self)
        self._map = BonkMap.decode_from_database('ILAcJAhBFBjBzCIDCAbAcgBwEYA1IDOAWgMrAAeAJgFYCiwytlAjEQGLoAMsAtm50gCmAdwbBIbACoBDAOrNh2AOIBVeAFlcATXIBJZAAtURJak4BpaMAASJAExsCW2eQPTRkACJFdITwDMANRB6RhZ2Ll5+JCgAdhjgX08PGKsYa0gE8WB0LLz8goKrCGZA7B4AVgNsWUCAa10OAHstfFR-AGoAeh7envAbLoA3Pr7O0d7waWxMOyzM4DYALxBhKjp4FSVXSiUiId4BQuO8roAWfOQugYTPLsl1JcfnlZO394-Pk7TgaFpMv4QegQZDCNh1LKeYAAeWKXwKMH+vyQgUksCUbAAzNg6pAiHlhJ4IfDCioAcCQGwVJjIAZKHYLkggA')

    async def disconnect(self) -> None:
        if self.is_connected:
            await self._socket.disconnect()
        if self.peer_ready:
            await self._peer.destroy()
        self._room_data = None
        self._total_players = 0
        self._peer_ready = False
        self._time_offset = None
        self._synced = False
        self._peer_id = None
        self._is_connected = False
        self._connections = []
        self._bot_player = None
        self._p2p_revert_task.cancel()
        try:
            await self._p2p_revert_task
        except asyncio.CancelledError:
            pass
        self._p2p_revert_task = None
        self._connect_event.clear()
        self._bot.remove_room(self)

    @property
    def map(self) -> BonkMap:
        return copy.deepcopy(self._map)

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
    def players(self) -> List['Player']:
        return self._room_data.players

    @property
    def has_password(self) -> bool:
        return self._room_data.password is not None

    @property
    def mode(self) -> 'Mode':
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
    def host(self) -> 'Player':
        return self._room_data.host

    @property
    def rounds(self) -> int:
        return self._room_data.rounds

    @property
    def team_state(self) -> 'TeamState':
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
    def server(self) -> 'Server':
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
    def bot(self) -> 'BonkBot':
        return self._bot

    @property
    def bot_player(self) -> 'Player':
        return self._bot_player

    def get_player_by_id(self, player_id: int) -> 'Player':
        return self._room_data.player_by_id(player_id)

    async def connect(self) -> None:
        if self.is_connected:
            await self._bot.dispatch('on_error', self.bot, RoomAlreadyConnected(self))
            return
        async def init_socket() -> None:
            await self._socket.connect(bonk_socket_api.format(self._server.name), transports=['websocket'])
            await self._make_timesync()
        await asyncio.gather(
            init_socket(),
            self._make_peer(),
        )
        self._p2p_revert_task = asyncio.create_task(self._handle_p2p_revert())

    async def _handle_p2p_revert(self) -> None:
        await self.wait_for_connection()
        while True:
            for player in self.players:
                num_player_moves = len(player.moves)
                start_index = num_player_moves - 1
                end_index = max(0, num_player_moves - 1000)
                for i in range(start_index, end_index, -1):
                    move = player.moves[i]
                    if move is None:
                        continue
                    time_since_move = time.time() - move.time
                    if time_since_move > 2000:
                        break
                    if move.time > 800 and move.by_peer and not move.by_socket and not move.peer_ignored and not move.reverted:
                        move.reverted = True
                        player.peer_reverts += 1
                        if player.peer_reverts >= 4:
                            player.peer_reverts = 0
                            player.peer_ban_level += 1
                            player.peer_ban_until = time.time() + 15000 * (2 ** player.peer_ban_level)
                        await self.bot.dispatch('on_move_revert', self, player, move)
            await asyncio.sleep(0.1)

    async def _init_connection(self) -> None:
        if self._action == RoomAction.CREATE:
            await self._create()
        else:
            await self._join()

    async def _create(self) -> None:
        name = self._room_params.name
        if name is None:
            name = f"{self._bot.name}'s game"
        data = {
            'peerID': self._peer_id,
            'roomName': name,
            'maxPlayers': self._room_params.max_players,
            'password': self._room_params.password,
            'id': self._bot.id,
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
            'avatar': self._bot.active_avatar.to_json(),
        }
        if self._bot.is_guest:
            data['guestName'] = self._bot.name
        else:
            data['token'] = self._bot.token
        self._bot_player = Player(
            bot=self._bot,
            room=self,
            id=0,
            team=Team.FFA,
            avatar=self._bot.active_avatar,
            name=self._bot.name,
            is_guest=self._bot.is_guest,
            level=self._bot.level,
            peer_id=self._peer_id,
            joined_with_bypass=None,
        )
        self._room_data = RoomData(
            name=name,
            host=self._bot_player,
            players=[self._bot_player],
        )
        self._total_players = 1
        await self._socket.emit(SocketEvents.Outgoing.CREATE_ROOM, data)

    async def _join(self) -> None:
        pass

    async def _make_timesync(self) -> None:
        self.timesyncer = TimeSyncer(
            interval=10,
            timeout=1,
            delay=0.25,
            repeat=5,
            socket=self._socket,
        )

        @self.timesyncer.event_emitter.on('sync')
        async def on_sync(state: str) -> None:
            if state == 'end' and not self._synced:
                self._synced = True
                if self.peer_ready:
                    await self._init_connection()

        @self.timesyncer.event_emitter.on('change')
        async def on_change(offset: int) -> None:
            if self._time_offset is not None:
                await self._bot.dispatch('on_time_offset_change', self, offset - self._time_offset)
            self._time_offset = offset

        await self.timesyncer.start()

    async def _make_peer(self) -> None:
        peer_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + '000000'
        self._peer = Peer(id=peer_id, options=PeerOptions(
            host=bonk_peer_api.format(self._server.name),
            port=443,
            path='/myapp',
            secure=True,
        ))

        @self._peer.on('open')
        async def on_open(peer_id: str) -> None:
            self._peer_ready = True
            self._peer_id = peer_id
            if self._synced:
                await self._init_connection()

        @self._peer.on('connection')
        async def on_connection(connection: DataConnection) -> None:
            self._peer_ready = True
            self._connections.append(connection)
            print(connection)
            for player in self._room_data.players:
                print(connection.peer)
                print(player.peer_id)
                if player.peer_id == connection.peer:
                    player.data_connection = connection
                    break
            await self._process_new_connection(connection)

        @self._peer.on('error')
        async def on_error(error: str) -> None:
            print(error)

        await self._peer.start()

    async def _process_new_connection(self, connection: BinaryPack) -> None:
        player = None
        def get_player() -> Player:
            nonlocal player
            if player is None:
                for iplayer in self._room_data.players:
                    if iplayer.peer_id == connection.peer:
                        player = iplayer
                        break
                return player

        async def on_data(data: Dict) -> None:
            player = get_player()
            if player.moves.get(data['c']) is not None:
                player.moves[data['c']].by_peer = True
            elif player.peer_ban_until > time.time():
                pass
            else:
                move = PlayerMove()
                move.time = time.time()
                move.frame = data['f']
                move.by_peer = True
                move.peer_ignored = False
                move.by_socket = False
                move.reverted = False
                move.unreverted = False
                move.inputs.flags = data['i']
                move.sequence = data['c']
                player.moves[move.sequence] = move
                await self.bot.dispatch('on_player_move', self, player, move)

        connection.on('data', lambda data: asyncio.create_task(on_data(data)))

    async def _init_player_peer(self, player: Player) -> None:
        player.data_connection = await self._peer.connect(player.peer_id)
        await self._process_new_connection(player.data_connection)

    async def wait_for_connection(self) -> None:
        await self._connect_event.wait()

    def _bind_listeners(self) -> None:
        @self.socket.event
        async def disconnect() -> None:
            await self.disconnect()

        @self.socket.on(SocketEvents.Incoming.PING_DATA)
        async def on_ping_data(pings: Dict, player_id: int) -> None:
            await self.socket.emit(SocketEvents.Outgoing.PING_DATA, {'id': player_id})
            for player_id, ping in pings.items():
                self._room_data.players[int(player_id)].ping = ping
            await self._bot.dispatch('on_ping_update', self)

        @self.socket.on(SocketEvents.Incoming.ROOM_CREATE)
        async def on_room_create(*args) -> None:
            await self._bot.dispatch('on_room_connection', self, RoomAction.CREATE)

        @self.socket.on(SocketEvents.Incoming.ROOM_JOIN)
        async def on_room_join(bot_id: int, host_id: int, players: Dict, timestamp: int, team_lock: bool,
                               join_id: int, join_bypass: str) -> None:
            self._room_data.join_id = f'{join_id:06}'
            self._room_data.join_bypass = join_bypass
            self._room_data.team_lock = team_lock
            self._total_players = len(players)
            for player_id, player_data in players.items():
                player = Player(
                    bot=self._bot,
                    room=self,
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
            self._is_connected = True
            self._connect_event.set()
            await self._bot.dispatch('on_room_connection', self, RoomAction.JOIN)

        @self.socket.on(SocketEvents.Incoming.PLAYER_JOIN)
        async def on_player_join(player_id: int, peer_id: str, username: str, is_guest: bool, level: int,
                                 joined_with_bypass: int, avatar: Dict) -> None:
            connection = None
            for data_connection in self._connections:
                if data_connection.peer == peer_id:
                    connection = data_connection
                    break
            player = Player(
                bot=self._bot,
                room=self,
                data_connection=connection,
                id=player_id,
                team=Team.FFA if self.team_state == TeamState.FFA and not self.team_lock else Team.SPECTATOR,
                avatar=Avatar.from_json(avatar),
                peer_id=peer_id,
                name=username,
                is_guest=is_guest,
                level=level,
                joined_with_bypass=joined_with_bypass,
            )
            self._room_data.players.append(player)
            self._total_players += 1
            await self._bot.dispatch('on_player_join', self, player)
            bal = [0] * self._total_players
            for player in self.players:
                bal[player.id] = player.balance
            await self._socket.emit(
                SocketEvents.Outgoing.INFORM_IN_LOBBY,
                {
                    'sid': player_id,
                    'gs': {
                        'map': self._map.to_json(),
                        'gt': 2,
                        'wl': self.rounds,
                        'q': False,
                        'tl': self.team_lock,
                        'tea': self.team_state != TeamState.FFA,
                        'ga': self.mode.engine,
                        'mo': self.mode.mode,
                        'bal': bal,
                    },
                })

        @self.socket.on(SocketEvents.Incoming.PLAYER_LEFT)
        async def on_player_left(player_id: int, data: Dict) -> None:
            player = self.get_player_by_id(player_id)
            self.players.remove(player)
            if player.data_connection and player.data_connection.open:
                await player.data_connection.close()
            await self.bot.dispatch('on_player_left', self, player)

        @self.socket.on(SocketEvents.Incoming.HOST_LEFT)
        async def on_host_left(old_host_id: int, new_host_id: int, data: Dict) -> None:
            old_host = self.get_player_by_id(old_host_id)
            new_host = self.get_player_by_id(new_host_id)
            self.players.remove(old_host)
            if old_host.data_connection and old_host.data_connection.open:
                await old_host.data_connection.close()
            self._room_data.host = new_host
            await self.bot.dispatch('on_host_left', self, old_host)

        @self.socket.on(SocketEvents.Incoming.PLAYER_INPUT)
        async def on_move(player_id: int, data: Dict) -> None:
            player = self.get_player_by_id(player_id)
            if player is None:
                return
            if player.moves.get(data['c']) is not None:
                move = player.moves[data['c']]
                move.by_socket = True
                if move.reverted:
                    move.unreverted = True
                    await self.bot.dispatch('on_player_move', self, player, move)
                elif move.peer_ignored:
                    await self.bot.dispatch('on_player_move', self, player, move)
            else:
                move = PlayerMove()
                move.time = time.time()
                move.frame = data['f']
                move.by_peer = False
                move.peer_ignored = False
                move.by_socket = True
                move.reverted = False
                move.unreverted = False
                player.moves[move.sequence] = move
                await self.bot.dispatch('on_player_move', self, player, move)

        @self.socket.on(SocketEvents.Incoming.READY_CHANGE)
        async def on_ready_change(player_id: int, state: bool) -> None:
            player = self.get_player_by_id(player_id)
            player.ready = state
            await self.bot.dispatch('on_ready_change', self, player)

        @self.socket.on(SocketEvents.Incoming.READY_RESET)
        async def on_ready_reset() -> None:
            for player in self.players:
                player.ready = False
            await self.bot.dispatch('on_ready_reset', self)

        @self.socket.on(SocketEvents.Incoming.PLAYER_MUTED)
        async def on_player_mute(player_id: int, data: dict) -> None:
            player = self.get_player_by_id(player_id)
            player.muted = True
            await self.bot.dispatch('on_player_mute', self, player)

        @self.socket.on(SocketEvents.Incoming.PLAYER_UNMUTED)
        async def on_player_unmute(player_id: int, data: dict) -> None:
            player = self.get_player_by_id(player_id)
            player.muted = False
            await self.bot.dispatch('on_player_unmute', self, player)

        @self.socket.on(SocketEvents.Incoming.PLAYER_NAME_CHANGE)
        async def on_player_name_change(player_id: int, new_name: str) -> None:
            player = self.get_player_by_id(player_id)
            old_name = player.name
            player.name = new_name
            await self.bot.dispatch('on_player_name_change', self, player, old_name)

        @self.socket.on(SocketEvents.Incoming.GAME_END)
        async def on_game_end() -> None:
            await self.bot.dispatch('on_game_end', self)

        @self.socket.on(SocketEvents.Incoming.GAME_START)
        async def on_game_start(unix_time: int, map_data: str, game_settings: dict) -> None:
            pair = StaticPair(PSON_KEYS)
            self._map = pair.decode(ByteBuffer().from_base64(map_data, case_encoded=True, lz_encoded=True))
            self._room_data.rounds = game_settings['wl']
            self._room_data.team_lock = game_settings['tl']
            self._room_data.mode = Mode.from_mode_code(game_settings['mo'])
            for player in self.players:
                if player.id >= len(game_settings['bal']):
                    player.balance = 0
                    continue
                player.balance = game_settings['bal'][player.id]
            if not game_settings['tea']:
                self._room_data.team_state = TeamState.FFA
            elif self._room_data.mode == Mode.FOOTBALL:
                self._room_data.team_state = TeamState.DUO
            else:
                self._room_data.team_state = TeamState.ALL
            await self.bot.dispatch('on_game_start', self, unix_time)

        @self.socket.on(SocketEvents.Incoming.PLAYER_TEAM_CHANGE)
        async def on_player_team_change(player_id: int, team: int) -> None:
            player = self.get_player_by_id(player_id)
            player.team = Team.from_number(team)
            await self.bot.dispatch('on_player_team_change', self, player)

        @self.socket.on(SocketEvents.Incoming.TEAM_LOCK)
        async def on_team_lock(state: bool) -> None:
            self._room_data.team_lock = state
            await self.bot.dispatch('on_team_lock', self)

        @self.socket.on(SocketEvents.Incoming.MESSAGE)
        async def on_message(player_id: int, message: str) -> None:
            player = self.get_player_by_id(player_id)
            await self.bot.dispatch('on_message', self, player, message)

        @self.socket.on(SocketEvents.Incoming.STATUS)
        async def on_error(error: str) -> None:
            if error != RATE_LIMIT_PONG:
                await self.bot.dispatch('on_error', self.bot, ApiError(ErrorType.RATE_LIMITED))

            if error in CRITICAL_API_ERRORS:
                await self.disconnect()
        
        @self.socket.on(SocketEvents.Incoming.LEVEL_UP)
        async def on_level_up(data: dict) -> None:
            player = self.get_player_by_id(data['sid'])
            player.level = data['lv']
            await self.bot.dispatch('on_level_up', self, player)

        @self.socket.on(SocketEvents.Incoming.XP_GAIN)
        async def on_xp_gain(data: dict) -> None:
            new_xp = data['newXP']
            self._bot.update_xp(new_xp)
            if 'newToken' in data:
                self._bot.update_token(data['newToken'])

            await self._bot.dispatch('on_xp_gain', self, new_xp)

        @self.socket.on(SocketEvents.Incoming.ROOM_ID_OBTAIN)
        async def on_room_id_obtain(join_id: int, join_bypass: str) -> None:
            self._room_data.join_id = f'{join_id:06}'
            self._room_data.join_bypass = join_bypass
            self._is_connected = True
            self._connect_event.set()
            await self._bot.dispatch('on_room_id_obtain', self)

    async def gain_xp(self) -> None:
        """Get 100 xp. Limit 18000 in day, 2000 in 20 minutes"""
        await self.socket.emit(SocketEvents.Outgoing.XP_GAIN)
