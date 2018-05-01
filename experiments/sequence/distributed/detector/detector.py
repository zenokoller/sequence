from array import array
from asyncio import Queue
from collections import deque
from functools import partial
from itertools import chain
from typing import Callable, Iterable, Tuple, Sequence

from estimator.events import Events
from synchronizer.sync_event import SyncEvent
from utils.pairwise import pairwise

MISSING_MAXLEN = 10
Missing = array


async def detector(seed: int, queue: Queue, sequence_cls: Callable, report: Callable):
    sequence = sequence_cls(seed)
    get_actual_expected = partial(sync_event_to_actual_expected, sequence=sequence)
    missing = deque(maxlen=MISSING_MAXLEN)

    while True:
        sync_event = await queue.get()
        for actual, expected in get_actual_expected(sync_event):
            events, new_missing = detect_events(actual, expected, missing)
            missing.append(new_missing)
            report(events)


def sync_event_to_actual_expected(sync_event: SyncEvent, sequence: Sequence = None) -> Iterable:
    # TODO: Define return type (we also need timing information)
    lost_index, buffer, matches = sync_event
    actual_indices = chain.from_iterable(
        [[0], *((m.a, m.a + m.size) for m in matches[:-1]), matches[-1].a])
    expected_indices = chain.from_iterable(
        [[lost_index], *((m.b, m.b + m.size) for m in matches[-1]), matches[-1].b])
    actuals = (batch[i:j] for batch, (i, j) in zip(buffer, pairwise(actual_indices)))
    expecteds = (sequence[i:j] for i, j in pairwise(expected_indices))
    return zip(actuals, expecteds)


def detect_events(actual, expected, missing) -> Tuple[Events, Missing]:
    raise NotImplementedError
