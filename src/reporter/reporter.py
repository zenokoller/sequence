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
