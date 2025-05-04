import asyncio
import inspect
from typing import Any, Callable, Coroutine

from pymitter import EventEmitter


class BotEventHandler:
    event_emitter: EventEmitter

    def __init__(self):
        self.event_emitter = EventEmitter()

        @self.event_emitter.on('error')
        async def on_error(error: Exception):
            raise error

    def event(self, function: Callable[..., Coroutine[Any, Any, Any]]) -> None:
        if not asyncio.iscoroutinefunction(function):
            raise TypeError("Event handler function is not a coroutine ( must be defined with 'async def' )")

        attribute_name = "_" + function.__name__
        try:
            handler = getattr(self, attribute_name)
        except AttributeError as err:
            raise AttributeError(f"No event named {function.__name__} found") from err

        func_sig = inspect.signature(function)
        handler_sig = inspect.signature(handler)

        handler_params = list(handler_sig.parameters.values())[1:]
        func_params = list(func_sig.parameters.values())

        if len(func_params) != len(handler_params):
            raise TypeError(
                f"Handler expected to get {len(handler_params)} arguments, but got {len(func_params)}"
            )

        self.event_emitter.on(function.__name__.replace("on_", ""), function)

    async def _on_error(self, error: Exception) -> None:
        pass
