from array import array
from asyncio import Queue
from difflib import SequenceMatcher
from functools import partial
from itertools import chain
from typing import Callable, Iterable, Sequence, List, Match

from detector.detect_events import detect_losses, DetectInput
from synchronizer.sync_event import SyncEvent
from utils.iteration import pairwise


async def detector(seed: int, sync_queue: Queue, reporter_queue: Queue, sequence_cls: Callable):
    sequence = sequence_cls(seed)
    pieces_between_matches = partial(_pieces_between_matching_blocks, sequence=sequence)

    while True:
        sync_event = await sync_queue.get()
        for offset, actual, expected in pieces_between_matches(sync_event):
            for event in detect_losses(offset, actual, expected, sync_event.offsets[1]):
                await reporter_queue.put(event)


def _pieces_between_matching_blocks(sync_event: SyncEvent, sequence: Sequence = None) -> \
        Iterable[DetectInput]:
    (lost_offset, found_offset), buffer = sync_event

    expected = sequence[lost_offset:found_offset]
    matches = get_matching_blocks(sync_event.buffer.array, expected)

    actual_indices = chain.from_iterable(
        [[0], *((m.a, m.a + m.size) for m in matches), [len(buffer)]])
    expected_indices = chain.from_iterable(
        [[0], *((m.b, m.b + m.size) for m in matches), [len(expected)]])

    actual = (buffer[i:j] for i, j in pairwise(actual_indices))
    offset_with_expected = ((lost_offset + i, sequence[i:j]) for i, j in pairwise(expected_indices))
    return ((off, act, exp) for act, (off, exp) in zip(actual, offset_with_expected)
            if not len(act) == len(exp) == 0)


def get_matching_blocks(actual: array, expected: array) -> List[Match]:
    sequence_matcher = SequenceMatcher()
    sequence_matcher.set_seqs(actual, expected)
    return sequence_matcher.get_matching_blocks()
