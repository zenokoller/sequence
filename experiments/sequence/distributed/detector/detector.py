from asyncio import Queue
from functools import partial
from itertools import chain
from typing import Callable, Iterable, Sequence

from detector.detect_events import detect_losses, DetectInput
from synchronizer.sync_event import SyncEvent
from utils.iteration import pairwise


async def detector(seed: int, queue: Queue, sequence_cls: Callable, report: Callable):
    sequence = sequence_cls(seed)
    pieces_between_matches = partial(_pieces_between_matches, sequence=sequence)

    while True:
        sync_event = await queue.get()
        for lost_offset, actual, expected in pieces_between_matches(sync_event):
            for event in detect_losses(lost_offset, actual, expected):
                report(event)


def _pieces_between_matches(sync_event: SyncEvent, sequence: Sequence = None) -> \
        Iterable[DetectInput]:
    (lost_offset, found_offset), buffer, matches = sync_event
    bs = buffer.batch_size
    actual_indices = chain.from_iterable([[0], *((i * bs + m.a, i * bs + m.a + m.size) for i, m in
                                                 enumerate(matches)), [len(buffer)]])
    expected_indices = chain.from_iterable([[lost_offset], *((m.b, m.b + m.size) for m in matches),
                                            [found_offset]])

    actual = (buffer[i:j] for i, j in pairwise(actual_indices))
    offset_with_expected = ((i, sequence[i:j]) for i, j in pairwise(expected_indices))
    return ((off, act, exp) for act, (off, exp) in zip(actual, offset_with_expected)
            if not len(act) == len(exp) == 0)
