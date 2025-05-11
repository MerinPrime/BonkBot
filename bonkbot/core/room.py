import asyncio
import copy
import dataclasses
import random
import string
import time
from typing import TYPE_CHECKING, Dict, List, Optional, Union

import socketio
from peerjs_py import Peer, PeerOptions
from peerjs_py.dataconnection.BufferedConnection.BinaryPack import BinaryPack
from peerjs_py.dataconnection.DataConnection import DataConnection

from ..core.player import Player
from ..pson import ByteBuffer, StaticPair
from ..types import Inputs
from ..types.avatar import Avatar
from ..types.errors import ApiError, ErrorType
from ..types.errors.room_already_connected import RoomAlreadyConnected
from ..types.map.bonkmap import BonkMap
from ..types.mode import Mode
from ..types.player_move import PlayerMove
from ..types.room.room_action import RoomAction
from ..types.room.room_create_params import RoomCreateParams
from ..types.room.room_data import RoomData
from ..types.server import Server
from ..types.team import Team, TeamState
from . import PROTOCOL_VERSION
from .api import (
    CRITICAL_API_ERRORS,
    PSON_KEYS,
    RATE_LIMIT_PONG,
    SocketEvents,
    bonk_peer_api,
    bonk_socket_api,
    room_link_api,
)
from .timesyncer import TimeSyncer

if TYPE_CHECKING:
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
    sequence: int

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
        self.sequence = 0

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
        self.sequence = 0
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

    @property
    def is_host(self) -> bool:
        return self.bot_player.is_host

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
                    if time_since_move > 800 and move.by_peer and not move.by_socket and not move.peer_ignored and not move.reverted:
                        move.reverted = True
                        player.peer_reverts += 1
                        if player.peer_reverts >= 4:
                            player.peer_reverts = 0
                            player.peer_ban_level += 1
                            player.peer_ban_until = time.time() + 15000 * (2 ** player.peer_ban_level)
                        asyncio.create_task(self.bot.dispatch('on_move_revert', self, player, move))
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
        password = self._room_params.password
        if password is None:
            password = ''
        bypass = self._room_params.bypass
        if bypass is None:
            bypass = ''
        data = {
            'joinID': self._room_params.room_id,
            'roomPassword': password,
            'guest': self.bot.is_guest,
            'dbid': 2,
            'version': PROTOCOL_VERSION,
            'peerID': self._peer_id,
            'bypass': bypass,
            'avatar': self._bot.active_avatar.to_json(),
        }
        if self.bot.is_guest:
            data['guestName'] = self.bot.name
        else:
            data['token'] = self.bot.token
        self._room_data = RoomData(
            name=self._room_params.name,
            host=self._bot_player,
            players=[self._bot_player],
        )
        self._total_players = 1
        await self._socket.emit(SocketEvents.Outgoing.JOIN_ROOM, data)

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
            for player in self._room_data.players:
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

        @connection.on('data')
        def on_data(data: Dict) -> None:
            player = get_player()
            if player is None:
                return
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
                asyncio.create_task(self.bot.dispatch('on_player_move', self, player, copy.deepcopy(move)))

    async def _init_player_peer(self, player: Player) -> None:
        player.data_connection = await self._peer.connect(player.peer_id)
        await self._process_new_connection(player.data_connection)

    async def wait_for_connection(self) -> None:
        await self._connect_event.wait()

    def _set_game_settings(self, game_settings: dict) -> None:
        self._map = BonkMap.decode_from_database(game_settings['map'])
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

    def _bind_listeners(self) -> None:
        @self.socket.event
        async def disconnect() -> None:
            await self.disconnect()

        @self.socket.on(SocketEvents.Incoming.PING_DATA)
        async def on_ping_data(pings: Dict, player_id: int) -> None:
            await self.socket.emit(SocketEvents.Outgoing.PING_DATA, {'id': player_id})
            for player_id, ping in pings.items():
                self.get_player_by_id(int(player_id)).ping = ping
            await self._bot.dispatch('on_ping_update', self)

        @self.socket.on(SocketEvents.Incoming.ROOM_CREATE)
        async def on_room_create(*args) -> None:
            await self._bot.dispatch('on_room_connection', self, RoomAction.CREATE)

        @self.socket.on(SocketEvents.Incoming.ROOM_JOIN)
        async def on_room_join(bot_id: int, host_id: int, players: List, timestamp: int, team_lock: bool,
                               join_id: int, join_bypass: str, *args) -> None:
            self._room_data.join_id = f'{join_id:06}'
            self._room_data.join_bypass = join_bypass
            self._room_data.team_lock = team_lock
            self._total_players = len(players)
            for i, player_data in enumerate(players):
                if player_data is None:
                    self._room_data.players.append(Player(
                        bot=self.bot,
                        room=self,
                        id=i,
                        team=Team.SPECTATOR,
                        avatar=Avatar(),
                        peer_id='',
                        name='Unknown',
                        is_guest=True,
                        level=0,
                    ))
                    continue
                player = Player(
                    bot=self._bot,
                    room=self,
                    id=i,
                    team=Team.from_number(player_data['team']),
                    avatar=Avatar.from_json(player_data['avatar']),
                    peer_id=player_data['peerID'],
                    name=player_data['userName'],
                    is_guest=player_data['guest'],
                    ready=player_data['ready'],
                    tabbed=player_data['tabbed'],
                    level=player_data['level'],
                    joined_with_bypass=None,
                )
                if i == bot_id:
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
            await self._bot.dispatch('on_player_join', self, player)

        @self.socket.on(SocketEvents.Incoming.PLAYER_LEFT)
        async def on_player_left(player_id: int, data: Dict) -> None:
            player = self.get_player_by_id(player_id)
            player.left = True
            if player.data_connection and player.data_connection.open:
                await player.data_connection.close()
            await self.bot.dispatch('on_player_left', self, player)

        @self.socket.on(SocketEvents.Incoming.HOST_LEFT)
        async def on_host_left(old_host_id: int, new_host_id: int, data: Dict) -> None:
            old_host = self.get_player_by_id(old_host_id)
            if new_host_id == -1:
                await self.bot.dispatch('on_host_left', self, old_host)
                await self.disconnect()
                return
            new_host = self.get_player_by_id(new_host_id)
            old_host.left = True
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
                    asyncio.create_task(self.bot.dispatch('on_player_move', self, player, copy.deepcopy(move)))
                elif move.peer_ignored:
                    asyncio.create_task(self.bot.dispatch('on_player_move', self, player, copy.deepcopy(move)))
            else:
                move = PlayerMove()
                move.time = time.time()
                move.frame = data['f']
                move.inputs.flags = data['i']
                move.sequence = data['c']
                move.by_peer = False
                move.peer_ignored = False
                move.by_socket = True
                move.reverted = False
                move.unreverted = False
                player.moves[move.sequence] = move
                asyncio.create_task(self.bot.dispatch('on_player_move', self, player, copy.deepcopy(move)))

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
            for player in self.players:
                player.moves.clear()

        @self.socket.on(SocketEvents.Incoming.GAME_START)
        async def on_game_start(unix_time: int, encoded_state: str, game_settings: dict) -> None:
            self._set_game_settings(game_settings)
            pair = StaticPair(PSON_KEYS)
            buffer = ByteBuffer().from_base64(encoded_state, case_encoded=True)
            initial_state = pair.decode(buffer)
            del initial_state['ms']
            del initial_state['mm']
            del initial_state['capZones']
            del initial_state['physics']
            await self.bot.dispatch('on_game_start', self, unix_time, initial_state)

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

        @self.socket.on(SocketEvents.Incoming.INFORM_IN_LOBBY)
        async def inform_in_lobby(game_settings: dict) -> None:
            self._set_game_settings(game_settings)

        @self.socket.on(SocketEvents.Incoming.ON_KICK)
        async def on_player_kick(player_id: int, is_ban: bool) -> None:
            player = self.get_player_by_id(player_id)
            if is_ban:
                await self.bot.dispatch('on_ban', self, player)
            else:
                await self.bot.dispatch('on_kick', self, player)
            if player.is_bot:
                await self.disconnect()

        @self.socket.on(SocketEvents.Incoming.MODE_CHANGE)
        async def on_mode_change(engine: str, mode: str) -> None:
            self._room_data.mode = Mode.from_mode_code(mode)
            await self.bot.dispatch('on_mode_change', self)

        @self.socket.on(SocketEvents.Incoming.ROUNDS_CHANGE)
        async def on_rounds_change(rounds: int) -> None:
            self._room_data.rounds = rounds
            await self.bot.dispatch('on_rounds_change', self)

        @self.socket.on(SocketEvents.Incoming.MAP_CHANGE)
        async def on_map_change(encoded_map: str) -> None:
            self._map = BonkMap.decode_from_database(encoded_map)
            await self.bot.dispatch('on_map_change', self)

        @self.socket.on(SocketEvents.Incoming.AFK_WARN)
        async def on_afk_warn() -> None:
            await self.bot.dispatch('on_afk_warn', self)

        @self.socket.on(SocketEvents.Incoming.MAP_SUGGEST_HOST)
        async def on_map_suggest_host(encoded_map: str, player_id: int) -> None:
            player = self.get_player_by_id(player_id)
            bonk_map = BonkMap.decode_from_database(encoded_map)
            await self.bot.dispatch('on_map_suggest_host', self, player, bonk_map)

        @self.socket.on(SocketEvents.Incoming.MAP_SUGGEST_CLIENT)
        async def on_map_suggest_client(name: str, author: str, player_id: int) -> None:
            player = self.get_player_by_id(player_id)
            await self.bot.dispatch('on_map_suggest_client', self, player, name, author)

        @self.socket.on(SocketEvents.Incoming.SET_BALANCE)
        async def on_set_balance(player_id: int, balance: int) -> None:
            player = self.get_player_by_id(player_id)
            player.balance = balance
            await self.bot.dispatch('on_set_balance', self, player)

        @self.socket.on(SocketEvents.Incoming.TEAMS_TOGGLE)
        async def on_teams_toggle(state: bool) -> None:
            if state and self.mode == Mode.FOOTBALL:
                self._room_data.team_state = TeamState.DUO
            elif state:
                self._room_data.team_state = TeamState.ALL
            else:
                self._room_data.team_state = TeamState.FFA
            await self.bot.dispatch('on_teams_toggle', self)

        @self.socket.on(SocketEvents.Incoming.REPLAY_RECORD)
        async def on_replay_record(player_id: int) -> None:
            player = self.get_player_by_id(player_id)
            await self.bot.dispatch('on_replay_record', self, player)

        @self.socket.on(SocketEvents.Incoming.HOST_CHANGE)
        async def on_host_change(data: dict) -> None:
            old_host = self.get_player_by_id(data['oldHost'])
            new_host = self.get_player_by_id(data['newHost'])
            self._room_data.host = new_host
            await self.bot.dispatch('on_host_change', self, old_host)

        @self.socket.on(SocketEvents.Incoming.FRIEND_REQUEST)
        async def on_friend_request(player_id: int) -> None:
            player = self.get_player_by_id(player_id)
            await self.bot.dispatch('on_friend_request', self, player)

        @self.socket.on(SocketEvents.Incoming.COUNTDOWN)
        async def on_countdown(number: int) -> None:
            await self.bot.dispatch('on_countdown', self, number)

        @self.socket.on(SocketEvents.Incoming.COUNTDOWN_ABORT)
        async def on_countdown_abort() -> None:
            await self.bot.dispatch('on_countdown_abort', self)

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

        @self.socket.on(SocketEvents.Incoming.INITIAL_STATE)
        async def on_initial_state(admin: list, frame: int, game_settings: str, inputs: List[Dict],
                                   random: List[int], encoded_state: str, state_id: int) -> None:
            self._set_game_settings(game_settings)
            for input_data in inputs:
                player = self.get_player_by_id(input_data['playerId'])
                inputs = Inputs()
                inputs.flags = input_data['i']
                player.prev_inputs.append((input_data['f'], inputs))
            pair = StaticPair(PSON_KEYS)
            buffer = ByteBuffer().from_base64(encoded_state, case_encoded=True)
            initial_state = pair.decode(buffer)
            del initial_state['ms']
            del initial_state['mm']
            del initial_state['capZones']
            del initial_state['physics']
            await self._bot.dispatch('on_initial_state', self, frame, random, initial_state, state_id)

        @self.socket.on(SocketEvents.Incoming.ROOM_ID_OBTAIN)
        async def on_room_id_obtain(join_id: int, join_bypass: str) -> None:
            self._room_data.join_id = f'{join_id:06}'
            self._room_data.join_bypass = join_bypass
            self._is_connected = True
            self._connect_event.set()
            await self._bot.dispatch('on_room_id_obtain', self)

        @self.socket.on(SocketEvents.Incoming.PLAYER_TABBED)
        async def on_player_tabbed(player_id: int, state: bool) -> None:
            player = self.get_player_by_id(player_id)
            player.tabbed = state
            await self._bot.dispatch('on_player_tabbed', self, player)

        @self.socket.on(SocketEvents.Incoming.ROOM_NAME_CHANGE)
        async def on_room_name_change(new_room_name: str) -> None:
            self._room_data.name = new_room_name
            await self._bot.dispatch('on_room_name_change', self)

        @self.socket.on(SocketEvents.Incoming.ROOM_PASS_CHANGE)
        async def on_room_pass_change(state: bool) -> None:
            if not self.bot_player.is_host:
                if state:
                    self._room_data.password = ''
                else:
                    self._room_data.password = None
            await self._bot.dispatch('on_room_pass_change', self)

    async def send_message(self, message: str) -> None:
        await self.socket.emit(SocketEvents.Outgoing.SEND_MESSAGE, {'message': message})

    async def set_ready(self, state: bool) -> None:
        self.bot_player.ready = state
        await self.socket.emit(SocketEvents.Outgoing.SET_READY, {'ready': state})

    async def reset_all_ready(self) -> None:
        if not self.is_host:
            await self.bot.dispatch('on_error', ApiError(ErrorType.NOT_HOST))
            return
        for player in self.players:
            player.ready = False
        await self.socket.emit(SocketEvents.Outgoing.RESET_READY)

    async def set_mode(self, mode: 'Mode') -> None:
        if not self.is_host:
            await self.bot.dispatch('on_error', ApiError(ErrorType.NOT_HOST))
            return
        await self.socket.emit(SocketEvents.Outgoing.SET_MODE, {'ga': mode.engine, 'mo': mode.mode})

    async def set_rounds(self, rounds: int) -> None:
        if not self.is_host:
            await self.bot.dispatch('on_error', ApiError(ErrorType.NOT_HOST))
            return
        await self.socket.emit(SocketEvents.Outgoing.SET_ROUNDS, {'w': rounds})

    async def set_team(self, team: Team) -> None:
        await self.socket.emit(SocketEvents.Outgoing.SET_TEAM, {'targetTeam': team})

    async def set_team_lock(self, state: bool) -> None:
        if not self.is_host:
            await self.bot.dispatch('on_error', ApiError(ErrorType.NOT_HOST))
            return
        await self.socket.emit(SocketEvents.Outgoing.SET_TEAM_LOCK, {'teamLock': state})

    async def set_map(self, bonk_map: BonkMap) -> None:
        # TODO: Implement
        ...

    async def request_map(self, bonk_map: BonkMap) -> None:
        # TODO: Implement
        ...

    async def set_teams(self, state: bool) -> None:
        if not self.is_host:
            await self.bot.dispatch('on_error', ApiError(ErrorType.NOT_HOST))
            return
        if state and self.mode == Mode.FOOTBALL:
            self._room_data.team_state = TeamState.DUO
        elif state:
            self._room_data.team_state = TeamState.ALL
        else:
            self._room_data.team_state = TeamState.FFA
        await self.socket.emit(SocketEvents.Outgoing.SET_TEAM_STATE, {'t': state})

    async def record_replay(self) -> None:
        await self.socket.emit(SocketEvents.Outgoing.RECORD_REPLAY)

    async def set_tabbed(self, state: bool) -> None:
        self.bot_player.tabbed = state
        await self.socket.emit(SocketEvents.Outgoing.CHANGE_ROOM_PASS, {'out': state})

    async def change_password(self, new_password: str) -> None:
        if not self.is_host:
            await self.bot.dispatch('on_error', ApiError(ErrorType.NOT_HOST))
            return
        self._room_data.password = new_password
        await self.socket.emit(SocketEvents.Outgoing.CHANGE_ROOM_PASS, {'newPass': new_password})

    async def change_name(self, new_name: str) -> None:
        if not self.is_host:
            await self.bot.dispatch('on_error', ApiError(ErrorType.NOT_HOST))
            return
        self._room_data.name = new_name
        await self.socket.emit(SocketEvents.Outgoing.CHANGE_ROOM_NAME, {'newName': new_name})

    async def gain_xp(self) -> None:
        """Get 100 xp. Limit 18000 in day, 2000 in 20 minutes"""
        await self.socket.emit(SocketEvents.Outgoing.XP_GAIN)

    async def move(self, frame: int, inputs: Inputs, sequence: Optional[int] = None) -> None:
        if sequence is None:
            sequence = self.sequence
            self.sequence += 1
        await self.socket.emit(
            SocketEvents.Outgoing.MOVE,
            {
                'i': inputs.flags,
                'f': frame,
                'c': sequence,
            },
        )
        move = PlayerMove()
        move.frame = frame
        move.inputs = inputs
        move.sequence = sequence
        move.time = time.time()
        self.bot_player.moves[self.sequence] = move
