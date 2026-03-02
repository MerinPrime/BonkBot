from __future__ import annotations

import asyncio
import inspect
import sys
from typing import Any, Callable, Coroutine, TypeVar

from pymitter import EventEmitter

if sys.version_info >= (3, 10):
    from typing import Concatenate, ParamSpec
else:
    from typing_extensions import Concatenate, ParamSpec

from .bot_events import BotEvents

EventArgs = ParamSpec('EventArgs')
EventOwner = TypeVar('EventOwner')
AnyAsyncFunction = Callable[..., Coroutine[Any, Any, Any]]


class BotEventHandler(BotEvents):
    __event_emitter: EventEmitter
    __events: dict[str, AnyAsyncFunction]
    __default_events: dict[str, AnyAsyncFunction]

    def __init__(self) -> None:
        self.__event_emitter = EventEmitter()

        self.__events = {}
        for name, method in inspect.getmembers(
            BotEvents,
            predicate=inspect.isfunction,
        ):
            if not name.startswith('on_'):
                continue
            self.__events[name] = method

        self.__default_events = {}
        for event in self.__events:
            base_method = getattr(BotEvents, event)
            method = getattr(self, event)
            self.on(base_method, method)
            if method.__func__ is base_method:
                self.__default_events[event] = method

    def event(
        self,
        function: Callable[EventArgs, Coroutine[Any, Any, Any]],
    ) -> Callable[EventArgs, Coroutine[Any, Any, Any]]:
        if not asyncio.iscoroutinefunction(function):
            raise TypeError(
                f"Handler '{function.__name__}' must be async (use 'async def')",
            )

        event_name = function.__name__
        if event_name not in self.__events:
            raise AttributeError(f'No event named {event_name} found')

        func_sig = inspect.signature(self.__events[event_name])
        handler_sig = inspect.signature(function)

        handler_params = list(handler_sig.parameters.values())
        func_params = list(func_sig.parameters.values())

        if len(func_params) - 1 != len(handler_params):
            raise TypeError(
                f'Handler expected to get {len(handler_params)} arguments, but got {len(func_params) - 1}',
            )

        if event_name in self.__default_events:
            self.__event_emitter.off(event_name, self.__default_events[event_name])
        self.__event_emitter.on(event_name, function)
        return function

    def on(
        self,
        event: Callable[Concatenate[EventOwner, EventArgs], Coroutine[Any, Any, Any]],
        function: Callable[EventArgs, Coroutine[Any, Any, Any]],
    ) -> Callable[EventArgs, Coroutine[Any, Any, Any]]:
        if not asyncio.iscoroutinefunction(function):
            raise TypeError(
                f"Handler '{function.__name__}' must be async (use 'async def')",
            )

        event_name = event.__name__

        if event_name not in self.__events:
            raise AttributeError(f'No event named {event_name} found')

        func_sig = inspect.signature(self.__events[event_name])
        handler_sig = inspect.signature(function)

        handler_params = list(handler_sig.parameters.values())
        func_params = list(func_sig.parameters.values())

        if len(func_params) - 1 != len(handler_params):
            raise TypeError(
                f'Handler expected to get {len(handler_params)} arguments, but got {len(func_params) - 1}',
            )

        if event_name in self.__default_events:
            self.__event_emitter.off(event_name, self.__default_events[event_name])
        self.__event_emitter.on(event_name, function)
        return function

    def unbind(self, function: AnyAsyncFunction) -> None:
        self.__event_emitter.off(function.__name__, function)

    def off(
        self,
        event: Callable[Concatenate[EventOwner, EventArgs], Coroutine[Any, Any, Any]],
        function: Callable[EventArgs, Coroutine[Any, Any, Any]],
    ) -> None:
        self.__event_emitter.off(event.__name__, function)

    async def dispatch(
        self,
        event: Callable[Concatenate[EventOwner, EventArgs], Coroutine[Any, Any, Any]],
        *args: EventArgs.args,
        **kwargs: EventArgs.kwargs,
    ) -> None:
        await self.__event_emitter.emit_async(event.__name__, *args, **kwargs)
