import asyncio
import time
from typing import Dict, Optional

import socketio
from pymitter import EventEmitter

from .api.socket_events import SocketEvents


class TimeSyncer:
    def __init__(self, interval: float, timeout: float, delay: float, repeat: int, socket: socketio.AsyncClient):
        self.interval = interval
        self.timeout = timeout
        self.delay = delay
        self.repeat = repeat
        self.socket = socket
        self.offset = 0
        self._time_sum = 0
        self._in_progress = 0
        self.sync_id = 0
        self._ids_time = {}
        self.event_emitter = EventEmitter()
        self._lock = asyncio.Lock()
        self._task = None

        self.socket.on(SocketEvents.Incoming.TIMESYNC, self.on_result)

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _sync_task(self) -> None:
        await self.sync(repeat=3, delay=0.1)
        while True:
            await asyncio.sleep(self.interval)
            await self.sync()

    async def start(self) -> None:
        await self.stop()
        self._task = asyncio.create_task(self._sync_task())

    def now(self) -> float:
        return time.time() * 1000 - self.offset

    async def sync(self, *, repeat: Optional[int] = None, delay: Optional[float] = None) -> None:
        if repeat is None:
            repeat = self.repeat
        if delay is None:
            delay = self.delay
        async with self._lock:
            self._in_progress += repeat
            await self.event_emitter.emit_async('sync', 'start')
            for _ in range(repeat):
                self._ids_time[self.sync_id] = self.now()
                await self.socket.emit(SocketEvents.Outgoing.TIMESYNC, {'jsonrpc': '2.0', 'id': self.sync_id, 'method': 'timesync'})
                await asyncio.sleep(delay)
                self.sync_id += 1

    async def on_result(self, data: Dict) -> None:
        self._in_progress -= 1
        t0 = self._ids_time[data['id']]
        t1 = self.now()
        ts = data['result']

        offset = t1 + (t1 - t0) / 2 - ts
        self._time_sum += offset

        del self._ids_time[data['id']]

        if self._in_progress == 0:
            mean_offset = int(self._time_sum / self.repeat)
            self.offset += mean_offset
            self._time_sum = 0
            await self.event_emitter.emit_async('change', mean_offset)
            await self.event_emitter.emit_async('sync', 'end')
