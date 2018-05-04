import logging
from array import array
from asyncio import Queue
from collections import deque
from functools import partial
from itertools import chain
from typing import Callable, Iterable, Tuple, Sequence

from detector.events import Events
from synchronizer.sync_event import SyncEvent
from utils.iteration import pairwise

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
            missing.extend(new_missing)
            report(events)


def sync_event_to_actual_expected(sync_event: SyncEvent, sequence: Sequence = None) \
        -> Iterable[Tuple[array, Tuple[int, array]]]:
    (lost_offset, found_offset), buffer, matches = sync_event
    bs = buffer.batch_size
    actual_indices = chain.from_iterable(
        [[0],
         *((i * bs + m.a, i * bs + m.a + m.size) for i, m in enumerate(matches)),
         [len(buffer)]])
    expected_indices = chain.from_iterable(
        [[lost_offset], *((m.b, m.b + m.size) for m in matches), [found_offset]])

    actuals = (buffer[i:j] for i, j in pairwise(actual_indices))
    expecteds = ((i, sequence[i:j]) for i, j in pairwise(expected_indices))
    return ((act, (off, exp)) for act, (off, exp) in zip(actuals, expecteds) if not len(act) == len(
        exp) == 0)


def detect_events(actual: array, expected: Tuple[int, array], missing) -> Tuple[Events, Missing]:
    """Signature subject to change, need to add timing information for expected symbols."""
    logging.info('detect_events called:')
    logging.info(f'actual={actual}')
    logging.info(f'expected={expected}')
    return None, []
