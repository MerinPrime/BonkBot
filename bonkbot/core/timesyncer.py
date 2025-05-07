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
        asyncio.create_task(self.stop())
    
    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _sync_task(self):
        try:
            while True:
                await self.sync()
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            pass

    async def start(self):
        self._task = asyncio.create_task(self._sync_task())

    def now(self):
        return time.time() * 1000 - self.offset

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

        offset = t1 + (t1 - t0) / 2 - ts
        self._time_sum += offset

        del self._ids_time[data['id']]

        if self._in_progress == 0:
            mean_offset = int(self._time_sum / self.repeat)
            self.offset += mean_offset
            self._time_sum = 0
            print(self.offset)
            await self.event_emitter.emit_async('change', mean_offset)
            await self.event_emitter.emit_async('sync', 'end')
