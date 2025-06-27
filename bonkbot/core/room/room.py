import asyncio
import copy
import random
import string
import time
from asyncio import Event, Future, Task
from typing import TYPE_CHECKING, List, Optional, Union

from peerjs_py import Peer, PeerOptions
from peerjs_py.dataconnection.DataConnection import DataConnection
from socketio import AsyncClient

from ...pson import ByteBuffer, StaticPair
from ...types.avatar import Avatar
from ...types.errors import ApiError, ErrorType
from ...types.errors.room_already_connected import RoomAlreadyConnected
from ...types.errors.room_not_connected import RoomNotConnected
from ...types.input import Inputs
from ...types.map.bonkmap import BonkMap, DEFAULT_MAP
from ...types.mode import Mode
from ...types.player_move import PlayerMove
from ...types.room.room_action import RoomAction
from ...types.room.room_create_params import RoomCreateParams
from ...types.room.room_data import RoomData
from ...types.team import Team, TeamState
from ..api.endpoints import (
    bonk_peer_api,
    bonk_socket_api,
    room_link_api,
)
from ..api.socket_events import SocketEvents
from ..bot.bot_event_handler import BotEventHandler
from ..constants import (
    CRITICAL_API_ERRORS,
    PROTOCOL_VERSION,
    PSON_KEYS,
    RATE_LIMIT_PONG,
)
from .player import Player
from .timesyncer import TimeSyncer

if TYPE_CHECKING:
    from peerjs_py.dataconnection.BufferedConnection.BinaryPack import BinaryPack

    from ...types.room.room_join_params import RoomJoinParams
    from ...types.server import Server
    from ..bot.bot import BonkBot

# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/network/NetworkEngine.ts
class Room:
    def __init__(self, bot: 'BonkBot', room_params: Union['RoomJoinParams', 'RoomCreateParams']) -> None:
        self._bot: BonkBot = bot
        self._room_params: Union[RoomJoinParams, RoomCreateParams] = room_params
        self._action: RoomAction = RoomAction.CREATE if isinstance(room_params, RoomCreateParams) else RoomAction.JOIN

        self._room_data: Optional[RoomData] = None
        self._socket: AsyncClient = None
        self._peer_ready: bool = False
        self._time_offset: int = None
        self._synced: bool = False
        self._peer_id: str = None
        self._is_connected: bool = False
        self._running: bool = False
        self._bot_player: Player = None
        self._p2p_revert_task: Task = None
        self._connections: List[BinaryPack] = []
        self._sequence: int = 0

    @property
    def map(self) -> 'BonkMap':
        return copy.deepcopy(self._room_data.map)

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
    def all_players_count(self) -> int:
        return len(self.all_players)

    @property
    def all_players(self) -> List['Player']:
        return self._room_data.players

    @property
    def players_count(self) -> int:
        return len(self.players)

    @property
    def players(self) -> List['Player']:
        return list(filter(lambda player: not player.is_left, self._room_data.players))

    @property
    def has_password(self) -> bool:
        return self._room_data.password is not None

    @property
    def mode(self) -> 'Mode':
        return self._room_data.mode

    @property
    def min_level(self) -> Optional[int]:
        return self._room_params.min_level

    @property
    def max_level(self) -> Optional[int]:
        return self._room_params.max_level

    @property
    def password(self) -> Optional[str]:
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
    def is_unlisted(self) -> Optional[bool]:
        return self._room_params.unlisted

    @property
    def socket(self) -> 'AsyncClient':
        return self._socket

    @property
    def server(self) -> 'Server':
        return self._room_params.server

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

    @property
    def is_running(self) -> bool:
        return self._running

    def get_player_by_id(self, player_id: int) -> 'Player':
        return self._room_data.player_by_id(player_id)

    async def connect(self) -> None:
        if self._running:
            raise RoomAlreadyConnected(self)
        self._running = True
        self._bot.add_room(self)
        self._socket = AsyncClient(ssl_verify=False)
        self.__bind_listeners()
        self._bind_sugar()
        async def init_socket() -> None:
            await self._socket.connect(bonk_socket_api.format(self._room_params.server.name), transports=['websocket'])
            await self._make_timesync()
        await asyncio.gather(
            init_socket(),
            self._make_peer(),
        )
        self._p2p_revert_task = asyncio.create_task(self._handle_p2p_revert())

    async def disconnect(self) -> None:
        if not self._running:
            raise RoomNotConnected(self)
        if self.timesyncer:
            await self.timesyncer.stop()
        if self._p2p_revert_task and not self._p2p_revert_task.done():
            self._p2p_revert_task.cancel()
            try:
                await self._p2p_revert_task
            except asyncio.CancelledError:
                pass
        if self._socket.connected:
            await self._socket.disconnect()
        if self.peer_ready:
            await self._peer.destroy()
        self._unbind_sugar()
        self._room_data = None
        self._socket = None
        self._peer_ready = False
        self._time_offset = None
        self._synced = False
        self._peer_id = None
        self._is_connected = False
        self._running = False
        self._bot_player = None
        self._p2p_revert_task = None
        self._connections = []
        self._sequence = 0
        self._bot.remove_room(self)

    async def _handle_p2p_revert(self) -> None:
        await self.wait_for_connection()
        while True:
            for player in self.players:
                num_player_moves = len(player.moves)
                start_index = num_player_moves - 1
                end_index = max(0, num_player_moves - 1000)
                for i in range(start_index, end_index, -1):
                    move = player.moves.get(i)
                    if move is None:
                        continue
                    time_since_move = time.time() - move.time
                    if time_since_move > 2:
                        break
                    if time_since_move > 0.8 and move.by_peer and not move.by_socket and not move.peer_ignored and not move.reverted:
                        move.reverted = True
                        player.peer_reverts += 1
                        if player.peer_reverts >= 4:
                            player.peer_reverts = 0
                            player.peer_ban_level += 1
                            player.peer_ban_until = time.time() + 15 * (2 ** player.peer_ban_level)
                        asyncio.create_task(self.bot.dispatch(BotEventHandler.on_move_revert, self, player, move))
            await asyncio.sleep(0.1)

    async def _init_connection(self) -> None:
        if self._action == RoomAction.CREATE:
            await self._create()
        else:
            await self._join()

    async def _create(self) -> None:
        data = {
            'peerID': self._peer_id,
            'roomName': self._room_params.name,
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
        )
        self._room_data = RoomData(
            name=self._room_params.name,
            host=self._bot_player,
            players=[self._bot_player],
            map=copy.deepcopy(DEFAULT_MAP),
        )
        await self._socket.emit(SocketEvents.Outgoing.CREATE_ROOM, data)

    async def _join(self) -> None:
        password = self._room_params.password
        if password is None:
            password = ''
        bypass = self._room_params.bypass
        if bypass is None:
            bypass = ''
        data = {
            'joinID': self._room_params.room_address,
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
            host=None,
            players=[],
        )
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
                if self._peer_ready:
                    await self._init_connection()

        @self.timesyncer.event_emitter.on('change')
        async def on_change(offset: int) -> None:
            if self._time_offset is not None:
                await self._bot.dispatch(BotEventHandler.on_time_offset_change, self, offset - self._time_offset)
            self._time_offset = offset

        await self.timesyncer.start()

    async def _make_peer(self) -> None:
        peer_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + '000000'
        self._peer = Peer(id=peer_id, options=PeerOptions(
            host=bonk_peer_api.format(self._room_params.server.name),
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
            self._connections.append(connection)
            for player in self.players:
                if player.peer_id == connection.peer:
                    player.data_connection = connection
                    break
            await self._process_new_connection(connection)

        @self._peer.on('error')
        async def on_error(error: str) -> None:
            raise error

        await self._peer.start()

    async def _process_new_connection(self, connection: 'BinaryPack') -> None:
        player = None
        def get_player() -> Player:
            nonlocal player
            if player is None:
                for iplayer in self.players:
                    if iplayer.peer_id == connection.peer:
                        player = iplayer
                        break
            return player

        @connection.on('data')
        def on_data(data: dict) -> None:
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
                asyncio.create_task(self.bot.dispatch(BotEventHandler.on_player_move, self, player, copy.deepcopy(move)))

    async def _init_player_peer(self, player: Player) -> None:
        player.data_connection = await self._peer.connect(player.peer_id)
        await self._process_new_connection(player.data_connection)

    def __bind_listeners(self) -> None:
        self.socket.on('disconnect', self.disconnect)
        self.socket.on(SocketEvents.Incoming.PING_DATA, self.__on_ping_data)
        self.socket.on(SocketEvents.Incoming.ROOM_CREATE, self.__on_room_create)
        self.socket.on(SocketEvents.Incoming.ROOM_JOIN, self.__on_room_join)
        self.socket.on(SocketEvents.Incoming.PLAYER_JOIN, self.__on_player_join)
        self.socket.on(SocketEvents.Incoming.PLAYER_LEFT, self.__on_player_left)
        self.socket.on(SocketEvents.Incoming.HOST_LEFT, self.__on_host_left)
        self.socket.on(SocketEvents.Incoming.PLAYER_MOVE, self.__on_move)
        self.socket.on(SocketEvents.Incoming.READY_CHANGE, self.__on_ready_change)
        self.socket.on(SocketEvents.Incoming.READY_RESET, self.__on_ready_reset)
        self.socket.on(SocketEvents.Incoming.PLAYER_MUTE, self.__on_player_mute)
        self.socket.on(SocketEvents.Incoming.PLAYER_UNMUTE, self.__on_player_unmute)
        self.socket.on(SocketEvents.Incoming.PLAYER_NAME_CHANGE, self.__on_player_name_change)
        self.socket.on(SocketEvents.Incoming.GAME_END, self.__on_game_end)
        self.socket.on(SocketEvents.Incoming.GAME_START, self.__on_game_start)
        self.socket.on(SocketEvents.Incoming.PLAYER_TEAM_CHANGE, self.__on_player_team_change)
        self.socket.on(SocketEvents.Incoming.TEAM_LOCK, self.__on_team_lock)
        self.socket.on(SocketEvents.Incoming.MESSAGE, self.__on_message)
        self.socket.on(SocketEvents.Incoming.INFORM_IN_LOBBY, self.__inform_in_lobby)
        self.socket.on(SocketEvents.Incoming.KICK, self.__on_player_kick)
        self.socket.on(SocketEvents.Incoming.MODE_CHANGE, self.__on_mode_change)
        self.socket.on(SocketEvents.Incoming.ROUNDS_CHANGE, self.__on_rounds_change)
        self.socket.on(SocketEvents.Incoming.MAP_CHANGE, self.__on_map_change)
        self.socket.on(SocketEvents.Incoming.AFK_WARN, self.__on_afk_warn)
        self.socket.on(SocketEvents.Incoming.MAP_SUGGEST_HOST, self.__on_map_suggest_host)
        self.socket.on(SocketEvents.Incoming.MAP_SUGGEST_CLIENT, self.__on_map_suggest_client)
        self.socket.on(SocketEvents.Incoming.SET_BALANCE, self.__on_set_balance)
        self.socket.on(SocketEvents.Incoming.TEAMS_TOGGLE, self.__on_teams_toggle)
        self.socket.on(SocketEvents.Incoming.REPLAY_RECORD, self.__on_replay_record)
        self.socket.on(SocketEvents.Incoming.HOST_CHANGE, self.__on_host_change)
        self.socket.on(SocketEvents.Incoming.FRIEND_REQUEST, self.__on_friend_request)
        self.socket.on(SocketEvents.Incoming.COUNTDOWN, self.__on_countdown)
        self.socket.on(SocketEvents.Incoming.COUNTDOWN_ABORT, self.__on_countdown_abort)
        self.socket.on(SocketEvents.Incoming.STATUS, self.__on_error)
        self.socket.on(SocketEvents.Incoming.LEVEL_UP, self.__on_level_up)
        self.socket.on(SocketEvents.Incoming.XP_GAIN, self.__on_xp_gain)
        self.socket.on(SocketEvents.Incoming.INFORM_IN_GAME, self.__inform_in_game)
        self.socket.on(SocketEvents.Incoming.ROOM_ID_OBTAIN, self.__on_room_id_obtain)
        self.socket.on(SocketEvents.Incoming.PLAYER_TABBED, self.__on_player_tabbed)
        self.socket.on(SocketEvents.Incoming.ROOM_NAME_CHANGE, self.__on_room_name_change)
        self.socket.on(SocketEvents.Incoming.ROOM_PASS_CHANGE, self.__on_room_pass_change)

    # region Events
    async def __on_ping_data(self, pings: dict, player_id: int) -> None:
        await self.socket.emit(SocketEvents.Outgoing.PING_DATA, {'id': player_id})
        for player_id, ping in pings.items():
            player = self.get_player_by_id(int(player_id))
            if player is None:
                continue
            player.ping = ping
        await self._bot.dispatch(BotEventHandler.on_ping_update, self)

    async def __on_room_create(self, *args) -> None:
        await self._bot.dispatch(BotEventHandler.on_room_connection, self, RoomAction.CREATE)
        await self._bot.dispatch(BotEventHandler.on_room_create, self)

    async def __on_room_join(self, bot_id: int, host_id: int, players: list, timestamp: int, team_lock: bool,
                           join_id: int, join_bypass: str, *args) -> None:
        self._room_data.join_id = f'{join_id:06}'
        self._room_data.join_bypass = join_bypass
        self._room_data.team_lock = team_lock
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
                    is_left=True,
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
            )
            if i == bot_id:
                self._bot_player = player
            else:
                self._bot.event_loop.create_task(self._init_player_peer(player))
            self._room_data.players.append(player)
        self._bot_player = self._room_data.player_by_id(bot_id)
        self._room_data.host = self._room_data.player_by_id(host_id)
        self._is_connected = True
        await self._bot.dispatch(BotEventHandler.on_room_connection, self, RoomAction.JOIN)
        await self._bot.dispatch(BotEventHandler.on_room_join, self)

    async def __on_player_join(self, player_id: int, peer_id: str, username: str, is_guest: bool, level: int,
                               team: int, avatar: dict) -> None:
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
            team=Team.from_number(team),
            avatar=Avatar.from_json(avatar),
            peer_id=peer_id,
            name=username,
            is_guest=is_guest,
            level=level,
        )
        self._room_data.players.append(player)
        await self._socket.emit(
            SocketEvents.Outgoing.INFORM_IN_LOBBY,
            {
                'sid': player_id,
                'gs': self._room_data.get_game_settings(),
            })
        await self._bot.dispatch(BotEventHandler.on_player_join, self, player)

    async def __on_player_left(self, player_id: int, timestamp: int) -> None:
        player = self.get_player_by_id(player_id)
        player.is_left = True
        if player.data_connection and player.data_connection.open:
            await player.data_connection.close()
        await self.bot.dispatch(BotEventHandler.on_player_left, self, player, timestamp)

    async def __on_host_left(self, old_host_id: int, new_host_id: int, timestamp: int) -> None:
        old_host = self.get_player_by_id(old_host_id)
        old_host.is_left = True
        if old_host.data_connection and old_host.data_connection.open:
            await old_host.data_connection.close()
        if new_host_id == -1:
            self._room_data.host = None
            await self.bot.dispatch(BotEventHandler.on_host_left, self, old_host, None, timestamp)
            await self.disconnect()
            return
        new_host = self.get_player_by_id(new_host_id)
        self._room_data.host = new_host
        await self.bot.dispatch(BotEventHandler.on_host_left, self, old_host, new_host, timestamp)

    async def __on_move(self, player_id: int, data: dict) -> None:
        player = self.get_player_by_id(player_id)
        if player.moves.get(data['c']) is not None:
            move = player.moves[data['c']]
            move.by_socket = True
            if move.reverted:
                move.unreverted = True
                asyncio.create_task(self.bot.dispatch(BotEventHandler.on_player_move, self, player, copy.deepcopy(move)))
            elif move.peer_ignored:
                asyncio.create_task(self.bot.dispatch(BotEventHandler.on_player_move, self, player, copy.deepcopy(move)))
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
            asyncio.create_task(self.bot.dispatch(BotEventHandler.on_player_move, self, player, copy.deepcopy(move)))

    async def __on_ready_change(self, player_id: int, state: bool) -> None:
        player = self.get_player_by_id(player_id)
        player.ready = state
        await self.bot.dispatch(BotEventHandler.on_ready_change, self, player)

    async def __on_ready_reset(self) -> None:
        for player in self.players:
            player.ready = False
        await self.bot.dispatch(BotEventHandler.on_ready_reset, self)

    async def __on_player_mute(self, player_id: int, data: dict) -> None:
        player = self.get_player_by_id(player_id)
        player.muted = True
        await self.bot.dispatch(BotEventHandler.on_player_mute, self, player)

    async def __on_player_unmute(self, player_id: int, data: dict) -> None:
        player = self.get_player_by_id(player_id)
        player.muted = False
        await self.bot.dispatch(BotEventHandler.on_player_unmute, self, player)

    async def __on_player_name_change(self, player_id: int, new_name: str) -> None:
        player = self.get_player_by_id(player_id)
        old_name = player.name
        player.name = new_name
        await self.bot.dispatch(BotEventHandler.on_player_name_change, self, player, old_name)

    async def __on_game_end(self) -> None:
        await self.bot.dispatch(BotEventHandler.on_game_end, self)
        for player in self.players:
            player.moves.clear()
            player.prev_inputs.clear()

    async def __on_game_start(self, unix_time: int, encoded_state: str, game_settings: dict) -> None:
        for player in self.players:
            player.moves.clear()
            player.prev_inputs.clear()
        self._room_data.set_game_settings(game_settings)
        pair = StaticPair(PSON_KEYS)
        buffer = ByteBuffer().from_base64(encoded_state, lz_encoded=True, case_encoded=True)
        initial_state = pair.decode(buffer)
        await self.bot.dispatch(BotEventHandler.on_game_start, self, unix_time, initial_state, game_settings)

    async def __on_player_team_change(self, player_id: int, team: int) -> None:
        player = self.get_player_by_id(player_id)
        player.team = Team.from_number(team)
        await self.bot.dispatch(BotEventHandler.on_player_team_change, self, player)

    async def __on_team_lock(self, state: bool) -> None:
        self._room_data.team_lock = state
        await self.bot.dispatch(BotEventHandler.on_team_lock, self)

    async def __on_message(self, player_id: int, message: str) -> None:
        player = self.get_player_by_id(player_id)
        await self.bot.dispatch(BotEventHandler.on_message, self, player, message)

    async def __on_player_kick(self, player_id: int, is_ban: bool) -> None:
        player = self.get_player_by_id(player_id)
        if is_ban:
            await self.bot.dispatch(BotEventHandler.on_ban, self, player)
        else:
            await self.bot.dispatch(BotEventHandler.on_kick, self, player)
        if player.is_bot:
            await self.disconnect()

    async def __on_mode_change(self, engine: str, mode: str) -> None:
        self._room_data.mode = Mode.from_mode_code(mode)
        await self.bot.dispatch(BotEventHandler.on_mode_change, self)

    async def __on_rounds_change(self, rounds: int) -> None:
        self._room_data.rounds = rounds
        await self.bot.dispatch(BotEventHandler.on_rounds_change, self)

    async def __on_map_change(self, encoded_map: str) -> None:
        self._room_data.map = BonkMap.decode_from_database(encoded_map)
        await self.bot.dispatch(BotEventHandler.on_map_change, self)

    async def __on_afk_warn(self) -> None:
        await self.bot.dispatch(BotEventHandler.on_afk_warn, self)

    async def __on_map_suggest_host(self, encoded_map: str, player_id: int) -> None:
        player = self.get_player_by_id(player_id)
        bonk_map = BonkMap.decode_from_database(encoded_map)
        await self.bot.dispatch(BotEventHandler.on_map_suggest_host, self, player, bonk_map)

    async def __on_map_suggest_client(self, name: str, author: str, player_id: int) -> None:
        player = self.get_player_by_id(player_id)
        await self.bot.dispatch(BotEventHandler.on_map_suggest_client, self, player, name, author)

    async def __on_set_balance(self, player_id: int, balance: int) -> None:
        player = self.get_player_by_id(player_id)
        player.balance = balance
        await self.bot.dispatch(BotEventHandler.on_set_balance, self, player)

    async def __on_teams_toggle(self, state: bool) -> None:
        if state and self.mode == Mode.FOOTBALL:
            self._room_data.team_state = TeamState.DUO
        elif state:
            self._room_data.team_state = TeamState.ALL
        else:
            self._room_data.team_state = TeamState.FFA
        await self.bot.dispatch(BotEventHandler.on_teams_toggle, self)

    async def __on_replay_record(self, player_id: int) -> None:
        player = self.get_player_by_id(player_id)
        await self.bot.dispatch(BotEventHandler.on_replay_record, self, player)

    async def __on_host_change(self, data: dict) -> None:
        old_host = self.get_player_by_id(data['oldHost'])
        new_host = self.get_player_by_id(data['newHost'])
        self._room_data.host = new_host
        await self.bot.dispatch(BotEventHandler.on_host_change, self, old_host)

    async def __on_friend_request(self, player_id: int) -> None:
        player = self.get_player_by_id(player_id)
        await self.bot.dispatch(BotEventHandler.on_friend_request, self, player)

    async def __on_countdown(self, number: int) -> None:
        await self.bot.dispatch(BotEventHandler.on_countdown, self, number)

    async def __on_countdown_abort(self) -> None:
        await self.bot.dispatch(BotEventHandler.on_countdown_abort, self)

    async def __on_error(self, error: str) -> None:
        if error != RATE_LIMIT_PONG:
            await self.bot.dispatch(BotEventHandler.on_error, self.bot, ApiError(ErrorType.from_string(error)))

        if error in CRITICAL_API_ERRORS:
            await self.disconnect()

    async def __on_level_up(self, data: dict) -> None:
        player = self.get_player_by_id(data['sid'])
        player.level = data['lv']
        await self.bot.dispatch(BotEventHandler.on_level_up, self, player)

    async def __on_xp_gain(self, data: dict) -> None:
        new_xp = data['newXP']
        self._bot.update_xp(new_xp)
        if 'newToken' in data:
            self._bot.update_token(data['newToken'])

        await self._bot.dispatch(BotEventHandler.on_xp_gain, self, new_xp)

    async def __inform_in_lobby(self, game_settings: dict) -> None:
        self._room_data.set_game_settings(game_settings)

    async def __inform_in_game(self, data: dict) -> None:
        encoded_state = data['state']
        state_id = data['stateID']
        random = data['random']
        inputs = data['inputs']
        frame = data['fc']
        self._room_data.set_game_settings(data['gs'])
        for input_data in inputs:
            player = self.get_player_by_id(input_data['p'])
            inputs = Inputs()
            inputs.flags = input_data['i']
            player.prev_inputs.append((input_data['f'], inputs))
        pair = StaticPair(PSON_KEYS)
        buffer = ByteBuffer().from_base64(encoded_state, case_encoded=True, lz_encoded=True)
        initial_state = pair.decode(buffer)
        await self._bot.dispatch(BotEventHandler.on_inform_in_game, self, frame, random, initial_state, state_id)

    async def __on_room_id_obtain(self, join_id: int, join_bypass: str) -> None:
        self._room_data.join_id = f'{join_id:06}'
        self._room_data.join_bypass = join_bypass
        self._is_connected = True
        await self._bot.dispatch(BotEventHandler.on_room_id_obtain, self)

    async def __on_player_tabbed(self, player_id: int, state: bool) -> None:
        player = self.get_player_by_id(player_id)
        player.tabbed = state
        await self._bot.dispatch(BotEventHandler.on_player_tabbed, self, player)

    async def __on_room_name_change(self, new_room_name: str) -> None:
        self._room_data.name = new_room_name
        await self._bot.dispatch(BotEventHandler.on_room_name_change, self)

    async def __on_room_pass_change(self, state: bool) -> None:
        if not self.bot_player.is_host:
            if state:
                self._room_data.password = ''
            else:
                self._room_data.password = None
        await self._bot.dispatch(BotEventHandler.on_room_pass_change, self)
    # endregion

    # region Sugar
    def _bind_sugar(self) -> None:
        self._connect_event = Event()
        self._any_player = Future()
        self._bot.on(BotEventHandler.on_room_id_obtain, self._sugar_on_room_id_obtain)
        self._bot.on(BotEventHandler.on_room_join, self._sugar_on_room_join)
        self._bot.on(BotEventHandler.on_player_join, self._sugar_on_player_join)

    def _unbind_sugar(self) -> None:
        self._bot.off(BotEventHandler.on_room_id_obtain, self._sugar_on_room_id_obtain)
        self._bot.off(BotEventHandler.on_room_join, self._sugar_on_room_join)
        self._bot.off(BotEventHandler.on_player_join, self._sugar_on_player_join)
        self._connect_event = None
        self._any_player = None

    async def wait_for_connection(self) -> None:
        await self._connect_event.wait()

    async def any_player(self) -> 'Player':
        if self._any_player.done():
            result = await self._any_player
            if result is None:
                self._any_player = Future()
                for player in self.players:
                    if player.is_bot:
                        continue
                    self._any_player.set_result(player)
                    break
        return await self._any_player

    async def _sugar_on_room_id_obtain(self, room: 'Room') -> None:
        if room != self:
            return
        self._connect_event.set()

    async def _sugar_on_room_join(self, room: 'Room') -> None:
        if room != self:
            return
        self._connect_event.set()

    async def _sugar_on_player_join(self, room: 'Room', player: 'Player') -> None:
        if room != self:
            return
        if self._any_player.done():
            return
        self._any_player.set_result(player)
    # endregion

    async def send_message(self, message: str) -> None:
        await self.socket.emit(SocketEvents.Outgoing.SEND_MESSAGE, {'message': message})

    async def set_ready(self, state: bool) -> None:
        self.bot_player.ready = state
        await self.socket.emit(SocketEvents.Outgoing.SET_READY, {'ready': state})

    async def reset_all_ready(self) -> None:
        if not self.is_host:
            raise ApiError(ErrorType.NOT_HOST)
        for player in self.players:
            player.ready = False
        await self.socket.emit(SocketEvents.Outgoing.RESET_READY)

    async def set_mode(self, mode: 'Mode') -> None:
        if not self.is_host:
            raise ApiError(ErrorType.NOT_HOST)
        await self.socket.emit(SocketEvents.Outgoing.SET_MODE, {'ga': mode.engine, 'mo': mode.mode})

    async def set_rounds(self, rounds: int) -> None:
        if not self.is_host:
            raise ApiError(ErrorType.NOT_HOST)
        await self.socket.emit(SocketEvents.Outgoing.SET_ROUNDS, {'w': rounds})

    async def set_team(self, team: Team) -> None:
        await self.socket.emit(SocketEvents.Outgoing.SET_TEAM, {'targetTeam': team})

    async def set_team_lock(self, state: bool) -> None:
        if not self.is_host:
            raise ApiError(ErrorType.NOT_HOST)
        await self.socket.emit(SocketEvents.Outgoing.SET_TEAM_LOCK, {'teamLock': state})

    async def set_map(self, bonk_map: 'BonkMap') -> None:
        # TODO: Implement
        ...

    async def request_map(self, bonk_map: 'BonkMap') -> None:
        # TODO: Implement
        ...

    async def set_teams(self, state: bool) -> None:
        if not self.is_host:
            raise ApiError(ErrorType.NOT_HOST)
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
        await self.socket.emit(SocketEvents.Outgoing.SET_TABBED, {'out': state})

    async def change_password(self, new_password: str) -> None:
        if not self.is_host:
            raise ApiError(ErrorType.NOT_HOST)
        self._room_data.password = new_password
        await self.socket.emit(SocketEvents.Outgoing.CHANGE_ROOM_PASS, {'newPass': new_password})

    async def change_name(self, new_name: str) -> None:
        if not self.is_host:
            raise ApiError(ErrorType.NOT_HOST)
        self._room_data.name = new_name
        await self.socket.emit(SocketEvents.Outgoing.CHANGE_ROOM_NAME, {'newName': new_name})

    async def gain_xp(self) -> None:
        """Get 100 xp. Limit 18000 in day, 2000 in 20 minutes"""
        await self.socket.emit(SocketEvents.Outgoing.XP_GAIN)

    async def move(self, frame: int, inputs: 'Inputs', sequence: Optional[int] = None) -> None:
        if sequence is None:
            sequence = self._sequence
            self._sequence += 1
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
        self.bot_player.moves[self._sequence] = move
