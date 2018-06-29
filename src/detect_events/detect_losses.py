from itertools import chain
from typing import Iterable, List

from detect_events.pairs_between_matches import pairs_between_matches
from detect_events.events import Event, Loss
from detect_events.types import Symbols
from sequence.sequence import Sequence
from synchronizer.sync_event import SyncEvent


def detect_losses(sync_event: SyncEvent, sequence: Sequence) -> Iterable[Event]:
    yield from chain.from_iterable(
        detect_for_pair(actual, expected, sync_event.found_offset)
        for actual, expected in pairs_between_matches(sync_event, sequence))


def detect_for_pair(actual: Symbols, expected: Symbols, found_offset: int) -> List[Loss]:
    if len(actual.symbols) == 0:
        return [Loss(expected.offset + i, found_offset) for i, _ in enumerate(expected.symbols)]
    else:
        return []


