import logging

from aiohttp import web

from detector.types import Loss, Event, Reordering
from reporter.reporter import Reporter

JSON_REPORTER_PORT = 9090


class HttpReporter(Reporter):
    """Simple reporter that collects packet and loss counts and exposes them as JSON on an HTTP
    endpoint."""

    def __init__(self, period):
        logging.getLogger('aiohttp.access').setLevel(logging.WARNING)
        self.period = int(period)
        self.packets = 0
        self.losses = 0
        self.reorderings = 0
        self._last_offset = 0

        app = web.Application()
        app.add_routes([web.get('/', self.handle_request)])
        self.runner = web.AppRunner(app)

    async def setup(self):
        await self.runner.setup()
        site = web.TCPSite(self.runner, port=JSON_REPORTER_PORT)
        await site.start()

    async def cleanup(self):
        await self.runner.cleanup()

    async def handle_event(self, event: Event):
        if isinstance(event, Loss):
            self.losses += 1
        elif isinstance(event, Reordering):
            self.reorderings += 1
        else:
            return
        self.packets += (event.offset - self._last_offset) % self.period
        self._last_offset = event.offset

    async def handle_request(self, request):
        return web.json_response({
            'packets': self.packets,
            'losses': self.losses,
            'reorderings': self.reorderings
        })
