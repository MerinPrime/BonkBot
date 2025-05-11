import asyncio
import inspect
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, List

from pymitter import EventEmitter

if TYPE_CHECKING:
    from ..core.player import Player
    from ..core.room import Room
    from ..types.map.bonkmap import BonkMap
    from ..types.player_move import PlayerMove
    from ..types.room.room_action import RoomAction
    from .bonkbot import BonkBot


class BotEventHandler:
    _event_emitter: EventEmitter
    _events: dict
    
    def __init__(self) -> None:
        self._event_emitter = EventEmitter()
        self._events = {}
        
        for name, method in inspect.getmembers(BotEventHandler, predicate=inspect.isfunction):
            if name.startswith('on_'):
                self._events[name] = method
        
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith('on_') and name in self._events:
                self.event(method)

    def event(self, function: Callable[..., Coroutine[Any, Any, Any]]) -> None:
        if not asyncio.iscoroutinefunction(function):
            raise TypeError("Handler '{function.__name__}' must be async (use 'async def')")

        event_name = function.__name__
        
        if event_name not in self._events:
            raise AttributeError(f'No event named {event_name} found')

        func_sig = inspect.signature(self._events[event_name])
        handler_sig = inspect.signature(function)

        handler_params = len(list(handler_sig.parameters.values()))
        func_params = len(list(func_sig.parameters.values())) - 1

        if func_params != handler_params:
            raise TypeError(
                f'Handler expected to get {handler_params} arguments, but got {func_params}',
            )

        self._event_emitter.off(event_name, self._events[event_name])
        self._event_emitter.on(event_name, function)

    async def dispatch(self, event: str, *args, **kwargs) -> None:
        await self._event_emitter.emit_async(event, *args, **kwargs)

    async def on_ready(self, bot: 'BonkBot') -> None:
        pass

    async def on_logout(self, bot: 'BonkBot') -> None:
        pass

    async def on_error(self, bot: 'BonkBot', error: Exception) -> None:
        raise error

    async def on_room_connection(self, room: 'Room', action: 'RoomAction') -> None:
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

    async def on_player_left(self, room: 'Room', player: 'Player') -> None:
        pass

    async def on_host_left(self, room: 'Room', player: 'Player') -> None:
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

    async def on_game_start(self, room: 'Room', unix_time: int) -> None:
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

    async def on_initial_state(self, room: 'Room', frame: int, random: List[int], initial_state: Dict, state_id: int) -> None:
        pass

    async def on_player_tabbed(self, room: 'Room', player: 'Player') -> None:
        pass

    async def on_room_name_change(self, room: 'Room') -> None:
        pass

    async def on_room_pass_change(self, room: 'Room') -> None:
        pass
