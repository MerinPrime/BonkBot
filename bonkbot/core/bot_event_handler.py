import asyncio
import inspect
from typing import Any, Callable, Coroutine

from pymitter import EventEmitter


class BotEventHandler:
    event_emitter: EventEmitter

    def __init__(self):
        self.event_emitter = EventEmitter()
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith("_on_"):
                self.event(method)

    def event(self, function: Callable[..., Coroutine[Any, Any, Any]]) -> None:
        if not asyncio.iscoroutinefunction(function):
            raise TypeError("Handler '{function.__name__}' must be async (use 'async def')")

        handler_attr = function.__name__
        is_default = handler_attr.startswith("_")
        event_name = handler_attr.lstrip("_") if is_default else handler_attr
        try:
            handler = getattr(self, f'_{event_name}')
        except AttributeError as err:
            raise AttributeError(f"No event named {handler_attr} found") from err

        func_sig = inspect.signature(function)
        handler_sig = inspect.signature(handler)

        handler_params = len(list(handler_sig.parameters.values()))
        func_params = len(list(func_sig.parameters.values()))

        if func_params != handler_params:
            print(function.__name__)
            raise TypeError(
                f"Handler expected to get {handler_params} arguments, but got {func_params}"
            )

        self.event_emitter.off(event_name, handler)
        self.event_emitter.on(event_name, function)

    async def _on_error(self, error: Exception) -> None:
        raise error

    async def _on_ready(self) -> None:
        pass
