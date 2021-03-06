import asyncio

from reporter.reporter import Reporter


class SilentReporter(Reporter):
    def __init__(self, *args):
        pass

    async def setup(self):
        await asyncio.sleep(0)

    async def run(self, queue: asyncio.Queue):
        await asyncio.sleep(0)

    async def handle_event(self, event):
        await asyncio.sleep(0)

    async def cleanup(self):
        await asyncio.sleep(0)
