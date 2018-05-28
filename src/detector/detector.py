from asyncio import Queue
from functools import partial
from typing import Callable

from detector.detect_losses import detect_losses

DEFAULT_DETECT_EVENTS = detect_losses


async def detector(seed: int, sync_queue: Queue, reporter_queue: Queue, sequence_cls: Callable,
                   detect_events: Callable = DEFAULT_DETECT_EVENTS):
    detect_events = partial(detect_events, sequence=sequence_cls(seed))
    while True:
        sync_event = await sync_queue.get()
        for event in detect_events(sync_event):
            await reporter_queue.put(event)
