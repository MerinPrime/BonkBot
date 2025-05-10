import asyncio
import inspect
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, List

from pymitter import EventEmitter

if TYPE_CHECKING:
    from ..types.map.bonkmap import BonkMap
    from ..core.player import Player
    from ..core.room import Room
    from ..types.player_move import PlayerMove
    from ..types.room.room_action import RoomAction
    from .bonkbot import BonkBot


class BotEventHandler:
    _event_emitter: EventEmitter

    def __init__(self) -> None:
        self._event_emitter = EventEmitter()
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith('_on_') or name.startswith('on_'):
                self.event(method)

    def event(self, function: Callable[..., Coroutine[Any, Any, Any]]) -> None:
        if not asyncio.iscoroutinefunction(function):
            raise TypeError("Handler '{function.__name__}' must be async (use 'async def')")

        handler_attr = function.__name__
        is_default = handler_attr.startswith('_')
        event_name = handler_attr.lstrip('_') if is_default else handler_attr
        try:
            handler = getattr(self, f'_{event_name}')
        except AttributeError as err:
            raise AttributeError(f'No event named {handler_attr} found') from err

        func_sig = inspect.signature(function)
        handler_sig = inspect.signature(handler)

        handler_params = len(list(handler_sig.parameters.values()))
        func_params = len(list(func_sig.parameters.values()))

        if func_params != handler_params:
            print(function.__name__)
            raise TypeError(
                f'Handler expected to get {handler_params} arguments, but got {func_params}',
            )

        self._event_emitter.off(event_name, handler)
        self._event_emitter.on(event_name, function)

    async def dispatch(self, event: str, *args, **kwargs) -> None:
        await self._event_emitter.emit_async(event, *args, **kwargs)

    async def _on_ready(self, bot: 'BonkBot') -> None:
        pass

    async def _on_logout(self, bot: 'BonkBot') -> None:
        pass

    async def _on_error(self, bot: 'BonkBot', error: Exception) -> None:
        raise error

    async def _on_room_connection(self, room: 'Room', action: 'RoomAction') -> None:
        pass

    async def _on_player_join(self, room: 'Room', player: 'Player') -> None:
        pass

    async def _on_xp_gain(self, room: 'Room', new_xp: int) -> None:
        pass

    async def _on_time_offset_change(self, room: 'Room', offset: int) -> None:
        pass

    async def _on_room_id_obtain(self, room: 'Room') -> None:
        pass

    async def _on_ping_update(self, room: 'Room') -> None:
        pass

    async def _on_level_up(self, room: 'Room', player: 'Player') -> None:
        pass

    async def _on_player_move(self, room: 'Room', player: 'Player', move: 'PlayerMove') -> None:
        pass

    async def _on_move_revert(self, room: 'Room', player: 'Player', move: 'PlayerMove') -> None:
        pass

    async def _on_player_left(self, room: 'Room', player: 'Player') -> None:
        pass

    async def _on_host_left(self, room: 'Room', player: 'Player') -> None:
        pass

    async def _on_ready_change(self, room: 'Room', player: 'Player') -> None:
        pass

    async def _on_ready_reset(self, room: 'Room') -> None:
        pass

    async def _on_player_mute(self, room: 'Room', player: 'Player') -> None:
        pass

    async def _on_player_unmute(self, room: 'Room', player: 'Player') -> None:
        pass

    async def _on_player_name_change(self, room: 'Room', player: 'Player', old_name: str) -> None:
        pass

    async def _on_game_end(self, room: 'Room') -> None:
        pass

    async def _on_game_start(self, room: 'Room', unix_time: int) -> None:
        pass

    async def _on_player_team_change(self, room: 'Room', player: 'Player') -> None:
        pass

    async def _on_team_lock(self, room: 'Room') -> None:
        pass

    async def _on_message(self, room: 'Room', player: 'Player', message: str) -> None:
        pass

    async def _on_ban(self, room: 'Room', player: 'Player') -> None:
        pass

    async def _on_kick(self, room: 'Room', player: 'Player') -> None:
        pass

    async def _on_mode_change(self, room: 'Room') -> None:
        pass

    async def _on_rounds_change(self, room: 'Room') -> None:
        pass

    async def _on_map_change(self, room: 'Room') -> None:
        pass

    async def _on_afk_warn(self, room: 'Room') -> None:
        pass

    async def _on_map_suggest_host(self, room: 'Room', player: 'Player', map: 'BonkMap') -> None:
        pass

    async def _on_map_suggest_client(self, room: 'Room', player: 'Player', name: str, author: str) -> None:
        pass

    async def _on_set_balance(self, room: 'Room', player: 'Player', balance: int) -> None:
        pass

    async def _on_teams_toggle(self, room: 'Room') -> None:
        pass

    async def _on_replay_record(self, room: 'Room', player: 'Player') -> None:
        pass

    async def _on_host_change(self, room: 'Room', old_host: 'Player') -> None:
        pass

    async def _on_countdown(self, room: 'Room', number: int) -> None:
        pass

    async def _on_countdown_abort(self, room: 'Room') -> None:
        pass

    async def _on_initial_state(self, room: 'Room', frame: int, random: List[int], initial_state: Dict, state_id: int) -> None:
        pass

    async def _on_player_tabbed(self, room: 'Room', player: 'Player') -> None:
        pass

    async def _on_room_name_change(self, room: 'Room') -> None:
        pass

    async def _on_room_pass_change(self, room: 'Room') -> None:
        pass
