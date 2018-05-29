import logging

from aiohttp import web

from detector.types import Loss
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

    async def handle_event(self, loss: Loss):
        if not isinstance(loss, Loss):
            return

        _, offset, _ = loss

        self.packets += (offset - self._last_offset) % self.period
        self.losses += 1

        self._last_offset = offset

    async def handle_request(self, request):
        return web.json_response({'packets': self.packets, 'losses': self.losses})
