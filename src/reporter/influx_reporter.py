import asyncio
from typing import List

import aiohttp

from detect_events.events import Loss, Receive, Event, Reordering
from reporter.reporter import Reporter


class InfluxReporterError(Exception):
    pass


DEFAULT_BATCH_SIZE = 1000

RECEIVE_LINE = 'receive offset={} {}'
LOSS_LINE = 'loss offset={},found_offset={} {}'
REORDERING_LINE = 'reordering offset={},amount={} {}'


class InfluxReporter(Reporter):
    """Sends events to InfluxDB via a POST request."""

    def __init__(self,
                 host: str = 'influxdb',
                 port: int = 8086,
                 db: str = 'telegraf',
                 batch_size: int = DEFAULT_BATCH_SIZE):
        """Reporter that sends all loss offsets to InfluxDB."""
        self._url = f'http://{host}:{port}/write?db={db}'
        self._batch: List[Event] = []
        self._batch_size = batch_size

    async def setup(self):
        self._session = aiohttp.ClientSession()

    async def handle_event(self, event: asyncio.Event):
        self._batch.append(event)
        if len(self._batch) >= self._batch_size:
            await self._flush_batch()

    async def _flush_batch(self):
        data = f'\n'.join(self._event_to_line(event) for event in self._batch).encode('utf-8')
        self._batch = []
        async with self._session.post(self._url, data=data) as resp:
            if resp.status != 204:
                raise InfluxReporterError(resp)

    def _event_to_line(self, event: Event) -> str:
        """Converts an event to InfluxDB's line protocol."""
        if isinstance(event, Receive):
            return RECEIVE_LINE.format(*event)
        elif isinstance(event, Loss):
            return LOSS_LINE.format(*event)
        elif isinstance(event, Reordering):
            return REORDERING_LINE.format(*event)
        else:
            raise NotImplementedError(f'Unknown event type: {type(event)}')

    async def cleanup(self):
        await self._flush_batch()
        if self._session:
            await self._session.close()
            self._session = None
