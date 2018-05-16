import asyncio

from detector.event import Event


class Reporter:
    async def setup(self):
        raise NotImplementedError

    async def run(self, queue: asyncio.Queue):
        while True:
            event = await queue.get()
            await self.handle_event(event)

    async def handle_event(self, event: Event):
        raise NotImplementedError

    async def cleanup(self):
        raise NotImplementedError


def start_reporter(reporter: Reporter) -> asyncio.Queue:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(reporter.setup())
    reporter_queue = asyncio.Queue()
    _ = asyncio.ensure_future(reporter.run(reporter_queue))
    return reporter_queue
