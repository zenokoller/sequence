import logging

from aiohttp import web

from detector.event import Loss
from reporter.reporter import Reporter

JSON_REPORTER_PORT = 9090


class JsonReporter(Reporter):
    """Simple reporter that collects packet and loss counts and exposes them as JSON on an
    endpoint."""

    def __init__(self, period: int):
        logging.getLogger('aiohttp.access').setLevel(logging.WARNING)
        self.period = period
        self.packets = 0
        self.losses = 0
        self._last_offset = 0

        app = web.Application()
        app.add_routes([web.get('/', self.handle_request)])
        self.runner = web.AppRunner(app)

    async def start(self):
        await self.runner.setup()
        site = web.TCPSite(self.runner, port=JSON_REPORTER_PORT)
        await site.start()

    async def stop(self):
        await self.runner.cleanup()

    async def send(self, loss: Loss):
        offset, size = loss

        self.packets += (offset - self._last_offset) % self.period
        self.losses += size

        self._last_offset = offset

    async def handle_request(self, request):
        return web.json_response({'packets': self.packets, 'losses': self.losses})
