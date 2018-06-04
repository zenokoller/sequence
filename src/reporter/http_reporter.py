import logging
from typing import Coroutine, Callable, Any

from aiohttp import web

from detector.events import Event
from reporter.accumulators.count import count_accumulator
from reporter.reporter import Reporter

HTTP_REPORTER_PORT = 9090
DEFAULT_ACCUMULATOR = count_accumulator


class HttpReporter(Reporter):
    """Simple reporter that handles event with an `accumulator` coroutine, which returns a `dict`.
    Said `dict` is exposed in JSON on an HTTP endpoint: `http://localhost:HTTP_REPORTER_PORT"""

    def __init__(self,
                 *accumulator_args,
                 accumulator: Callable[[Any], Coroutine[dict, Event, None]] = DEFAULT_ACCUMULATOR):
        logging.getLogger('aiohttp.access').setLevel(logging.WARNING)

        self.values = {}
        self.accumulator = accumulator(*accumulator_args)

        app = web.Application()
        app.add_routes([web.get('/', self.handle_request)])
        self.runner = web.AppRunner(app)

    async def setup(self):
        await self.runner.setup()
        site = web.TCPSite(self.runner, port=HTTP_REPORTER_PORT)
        await site.start()

    async def cleanup(self):
        await self.runner.cleanup()

    async def handle_event(self, event: Event):
        self.values = self.accumulator.send(event)

    async def handle_request(self, request):
        return web.json_response(self.values)
