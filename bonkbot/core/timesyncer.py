import asyncio
import time
from typing import Dict

import socketio
from pymitter import EventEmitter


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
        self.socket.on(23, self.on_result)
        self.event_emitter = EventEmitter()
        self._lock = asyncio.Lock()
        self._task = None

    def __del__(self):
        self._task.cancel()

    async def _sync_task(self):
        try:
            while True:
                await self.sync()
                await asyncio.sleep(self.delay)
        except asyncio.CancelledError:
            pass

    async def start(self):
        self._task = asyncio.create_task(self._sync_task())

    def now(self):
        return time.time() * 1000 + self.offset

    async def sync(self):
        async with self._lock:
            self._in_progress += self.repeat
            await self.event_emitter.emit_async('sync', 'start')
            for _ in range(self.repeat):
                self._ids_time[self.sync_id] = self.now()
                await self.socket.emit(18, {'jsonrpc': '2.0', 'id': self.sync_id, 'method': 'timesync'})
                await asyncio.sleep(self.delay)
                self.sync_id += 1

    async def on_result(self, data: Dict):
        self._in_progress -= 1
        t0 = self._ids_time[data['id']]
        t1 = self.now()
        ts = data['result']

        offset = ts - t1 + (t1 - t0) / 2
        self._time_sum += offset

        del self._ids_time[data['id']]

        if self._in_progress == 0:
            total_offset = int(self._time_sum / self.repeat)
            self.offset += total_offset
            self._time_sum = 0
            await self.event_emitter.emit_async('change', total_offset)
            await self.event_emitter.emit_async('sync', 'end')
