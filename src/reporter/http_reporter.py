import logging
from typing import Coroutine, Callable, Any

from aiohttp import web

from detector.events import Event, Reordering, Loss
from reporter.exceptions import ReporterError
from reporter.reporter import Reporter
from utils.coroutine import coroutine

HTTP_REPORTER_PORT = 9090


@coroutine
def count_accumulator(period) -> Coroutine[dict, Event, None]:
    """Accumulates packet, loss and reordering counts _without_ relying on explicit `Receive`
    events. Instead uses the difference in the offset of subsequent packets."""
    period = int(period)
    packets, losses, reorderings, _last_offset = 0, 0, 0, 0
    while True:
        event = yield {'packets': packets, 'losses': losses, 'reorderings': reorderings}
        if isinstance(event, Loss):
            losses += 1
        elif isinstance(event, Reordering):
            reorderings += 1
        else:
            raise ReporterError(f'Unexpected event: {event}')
        packets += (event.offset - _last_offset) % period
        _last_offset = event.offset


class HttpReporter(Reporter):
    """Simple reporter that handles event with an `accumulator` coroutine, which returns a `dict`.
    Said `dict` is exposed in JSON on an HTTP endpoint: `http://localhost:HTTP_REPORTER_PORT"""

    def __init__(self,
                 *accumulator_args,
                 accumulator: Callable[[Any], Coroutine[dict, Event, None]] = count_accumulator):
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
