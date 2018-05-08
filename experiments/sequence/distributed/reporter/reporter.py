from detector.event import Event


class Reporter:
    async def start(self):
        raise NotImplementedError

    async def send(self, event: Event):
        raise NotImplementedError

    async def stop(self):
        raise NotImplementedError
