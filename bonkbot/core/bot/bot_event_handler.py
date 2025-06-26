import asyncio
import inspect
from typing import TYPE_CHECKING, Any, Callable, Coroutine, List, Optional

from pymitter import EventEmitter

if TYPE_CHECKING:
    from ...types.map.bonkmap import BonkMap
    from ...types.player_move import PlayerMove
    from ...types.room.room_action import RoomAction
    from ..room.player import Player
    from ..room.room import Room
    from .bot import BonkBot


class BotEventHandler:
    __event_emitter: EventEmitter
    __events: dict

    def __init__(self) -> None:
        self.__event_emitter = EventEmitter()
        self.__events = {}

        for name, method in inspect.getmembers(BotEventHandler, predicate=inspect.isfunction):
            if name.startswith('on_'):
                self.__events[name] = method

        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith('on_') and name in self.__events:
                self.event(method)

    def event(self, function: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]:
        return self.on(function, function)

    def on(self, event: Callable[..., Coroutine[Any, Any, Any]],
           function: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]:
        if not asyncio.iscoroutinefunction(function):
            raise TypeError(f"Handler '{function.__name__}' must be async (use 'async def')")

        event_name = event.__name__

        if event_name not in self.__events:
            raise AttributeError(f'No event named {event_name} found')

        func_sig = inspect.signature(self.__events[event_name])
        handler_sig = inspect.signature(function)

        handler_params = len(list(handler_sig.parameters.values()))
        func_params = len(list(func_sig.parameters.values())) - 1

        if func_params != handler_params:
            raise TypeError(
                f'Handler expected to get {handler_params} arguments, but got {func_params}',
            )

        self.__event_emitter.off(event_name, self.__events[event_name])
        self.__event_emitter.on(event_name, function)
        return function

    def unbind(self, function: Callable[..., Coroutine[Any, Any, Any]]) -> None:
        self.__event_emitter.off(function.__name__, function)

    def off(self, event: Callable[..., Coroutine[Any, Any, Any]],
            function: Callable[..., Coroutine[Any, Any, Any]]) -> None:
        self.__event_emitter.off(event.__name__, function)

    async def dispatch(self, event: Callable[..., Coroutine[Any, Any, Any]], *args, **kwargs) -> None:
        await self.__event_emitter.emit_async(event.__name__, *args, **kwargs)

    async def on_ready(self, bot: 'BonkBot') -> None:
        pass

    async def on_logout(self, bot: 'BonkBot') -> None:
        pass

    async def on_error(self, bot: 'BonkBot', error: Exception) -> None:
        raise error

    async def on_room_connection(self, room: 'Room', action: 'RoomAction') -> None:
        pass

    async def on_room_create(self, room: 'Room') -> None:
        pass

    async def on_room_join(self, room: 'Room') -> None:
        pass

    async def on_player_join(self, room: 'Room', player: 'Player') -> None:
        pass

    async def on_xp_gain(self, room: 'Room', new_xp: int) -> None:
        pass

    async def on_time_offset_change(self, room: 'Room', offset: int) -> None:
        pass

    async def on_room_id_obtain(self, room: 'Room') -> None:
        pass

    async def on_ping_update(self, room: 'Room') -> None:
        pass

    async def on_level_up(self, room: 'Room', player: 'Player') -> None:
        pass

    async def on_player_move(self, room: 'Room', player: 'Player', move: 'PlayerMove') -> None:
        pass

    async def on_move_revert(self, room: 'Room', player: 'Player', move: 'PlayerMove') -> None:
        pass

    async def on_player_left(self, room: 'Room', player: 'Player', timestamp: int) -> None:
        """Called when non-host player leaves a room.
        
        :param room: The Room instance.
        :param player: The Player who left the room.
        :param timestamp: The server-provided Unix timestamp of the event, or
                          the game frame number if a match is in progress.
        :return: None
        
        Note: If the player who left was the host, this event will NOT be
        triggered. Instead, only the `on_host_left` event will be called.
        """
        pass

    async def on_host_left(self, room: 'Room', old_host: 'Player', new_host: Optional['Player'], timestamp: int) -> None:
        """Called when host leaves a room.
        
        :param room: The Room instance.
        :param old_host: The Player who was the host and has now left.
        :param new_host: The Player who has been promoted to the new host.
                         This will be `None` if the room was closed.
        :param timestamp: The server-provided Unix timestamp of the event, or
                          the game frame number if a match is in progress.
        :return: None
        """
        pass

    async def on_ready_change(self, room: 'Room', player: 'Player') -> None:
        pass

    async def on_ready_reset(self, room: 'Room') -> None:
        pass

    async def on_player_mute(self, room: 'Room', player: 'Player') -> None:
        pass

    async def on_player_unmute(self, room: 'Room', player: 'Player') -> None:
        pass

    async def on_player_name_change(self, room: 'Room', player: 'Player', old_name: str) -> None:
        pass

    async def on_game_end(self, room: 'Room') -> None:
        pass

    async def on_game_start(self, room: 'Room', unix_time: int, initial_state: dict, game_settings: dict) -> None:
        pass

    async def on_player_team_change(self, room: 'Room', player: 'Player') -> None:
        pass

    async def on_team_lock(self, room: 'Room') -> None:
        pass

    async def on_message(self, room: 'Room', player: 'Player', message: str) -> None:
        pass

    async def on_ban(self, room: 'Room', player: 'Player') -> None:
        pass

    async def on_kick(self, room: 'Room', player: 'Player') -> None:
        pass

    async def on_mode_change(self, room: 'Room') -> None:
        pass

    async def on_rounds_change(self, room: 'Room') -> None:
        pass

    async def on_map_change(self, room: 'Room') -> None:
        pass

    async def on_afk_warn(self, room: 'Room') -> None:
        pass

    async def on_map_suggest_host(self, room: 'Room', player: 'Player', map: 'BonkMap') -> None:
        pass

    async def on_map_suggest_client(self, room: 'Room', player: 'Player', name: str, author: str) -> None:
        pass

    async def on_set_balance(self, room: 'Room', player: 'Player', balance: int) -> None:
        pass

    async def on_teams_toggle(self, room: 'Room') -> None:
        pass

    async def on_replay_record(self, room: 'Room', player: 'Player') -> None:
        pass

    async def on_host_change(self, room: 'Room', old_host: 'Player') -> None:
        pass

    async def on_countdown(self, room: 'Room', number: int) -> None:
        pass

    async def on_countdown_abort(self, room: 'Room') -> None:
        pass

    async def on_inform_in_game(self, room: 'Room', frame: int, random: List[int], initial_state: dict, state_id: int) -> None:
        pass

    async def on_player_tabbed(self, room: 'Room', player: 'Player') -> None:
        pass

    async def on_room_name_change(self, room: 'Room') -> None:
        pass

    async def on_room_pass_change(self, room: 'Room') -> None:
        pass

    async def on_friend_request(self, room: 'Room', player: 'Player') -> None:
        pass
