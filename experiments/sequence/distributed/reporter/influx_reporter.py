import asyncio

import aiohttp

from detector.event import Loss, Receive, Event
from reporter.reporter import Reporter


class InfluxReporterError(Exception):
    pass


class InfluxReporter(Reporter):
    """Sends events to InfluxDB via a POST request."""

    def __init__(self,
                 host: str = 'influxdb',
                 port: int = 8086,
                 db: str = 'telegraf'):
        """Reporter that sends all loss offsets to InfluxDB."""
        self._url = f'http://{host}:{port}/write?db={db}'

    async def setup(self):
        self._session = aiohttp.ClientSession()

    async def handle_event(self, event: asyncio.Event):
        data = self._event_to_line(event)
        async with self._session.post(self._url, data=data) as resp:
            if resp.status == 204:
                return True
            else:
                raise InfluxReporterError(resp)

    def _event_to_line(self, event: Event) -> bytes:
        """Converts an event to InfluxDB's line protocol."""
        if isinstance(event, Receive):
            return f'receive offset={event.offset}'.encode('utf-8')
        elif isinstance(event, Loss):
            offset, size, found_offset = event
            if size == 1:
                return f'loss offset={offset},found_offset={found_offset}'.encode('utf-8')
            else:
                offsets = range(offset, offset + size)
                return b'\n'.join([f'loss offset={o},found_offset={found_offset}'.encode('utf-8')
                                   for o in offsets])
        else:
            # Reordering and duplicates yet to be implemented
            raise NotImplementedError

    async def cleanup(self):
        if self._session:
            await self._session.close()
            self._session = None
