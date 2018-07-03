from asyncio import Queue
from functools import partial
from typing import Callable

from detect_events.events import LostSync
from detect_events.exceptions import DetectorError
from detect_events.utils import DEFAULT_DETECT_EVENTS
from synchronizer.sync_event import SyncEvent, LostSyncEvent


async def detector(seed: int, sync_queue: Queue, reporter_queue: Queue, sequence_cls: Callable,
                   detect_events: Callable = DEFAULT_DETECT_EVENTS):
    detect_events = partial(detect_events, sequence=sequence_cls(seed))
    while True:
        sync_event = await sync_queue.get()
        if isinstance(sync_event, SyncEvent):
            for event in detect_events(sync_event):
                await reporter_queue.put(event)
        elif isinstance(sync_event, LostSyncEvent):
            await reporter_queue.put(LostSync(sync_event.lost_offset))
        else:
            raise DetectorError(f'Unexpected event: {event}')
