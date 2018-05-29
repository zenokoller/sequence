from itertools import chain
from typing import Iterable, Callable

from detector.missing_buffer import MissingBuffer
from detector.pairs_between_matches import pairs_between_matches
from detector.events import Event, Loss, Reordering
from detector.types import Symbols
from sequence.sequence import Sequence
from synchronizer.sync_event import SyncEvent


def get_detect_losses_and_reorderings(max_reorder_dist: int, max_size: int = None) -> Callable:
    missing = MissingBuffer(max_reorder_dist, max_size=max_size)

    def detect_for_pair(actual: Symbols, expected: Symbols, found_offset: int) -> Iterable[Event]:
        timed_out = missing.remove_timed_out(actual.offset)
        loss_events = (Loss(offset, found_offset) for offset in timed_out)

        reorder_events = []
        if len(actual.symbols) == 0:
            missing.append(expected)
        elif len(expected.symbols) == 0:
            reorder_events = missing.remove_if_found(actual)
        else:
            raise Exception('Did not expect both `actual` and `expected` to be nonempty!')

        return chain.from_iterable([loss_events, reorder_events])

    def detect(sync_event: SyncEvent, sequence: Sequence) -> Iterable[Event]:
        yield from adjust_reordering_amount(chain.from_iterable(
            detect_for_pair(actual, expected, sync_event.found_offset)
            for actual, expected in pairs_between_matches(sync_event, sequence)))

    return detect


def adjust_reordering_amount(events: Iterable[Event]) -> Iterable[Event]:
    """The amount of reordering is calculated with the offset of the found symbol in the
    sync event. Thus, we need to adjust the reordering amount by the number of lost packets
    before the reordering."""
    lost_count = 0
    for event in events:
        if isinstance(event, Loss):
            lost_count += 1
            yield event
        elif isinstance(event, Reordering):
            offset, amount, _ = event
            yield Reordering(offset, amount + lost_count)
        else:
            raise Exception('Did not expect another event type to be passed!')
