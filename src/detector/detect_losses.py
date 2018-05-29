from typing import Iterable, List

from detector.pairs_between_matches import pairs_between_matches
from detector.events import Event, Loss
from detector.types import Symbols
from sequence.sequence import Sequence
from synchronizer.sync_event import SyncEvent


def detect_losses(sync_event: SyncEvent, sequence: Sequence) -> Iterable[Event]:
    yield from (detect_for_pair(actual, expected, sync_event.found_offset)
                for actual, expected in pairs_between_matches(sync_event, sequence))


def detect_for_pair(actual: Symbols, expected: Symbols, found_offset: int) -> List[Loss]:
    if len(actual.symbols) == 0:
        return [Loss(expected.offset + i, found_offset) for i in range(len(expected))]
    else:
        return []
