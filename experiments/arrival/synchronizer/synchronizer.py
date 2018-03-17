from typing import Callable, Tuple, List, Optional, Iterable, NamedTuple

from synchronizer.exceptions import SynchronizationError

"""A synchronizer takes a signal and a reference and upon successful synchronization,
outputs a list of matches, where a match == (signal_offset, reference_offset)."""
Synchronizer = Callable[[Iterable, Iterable], Optional[List[Tuple[int, int]]]]

Range = Tuple[int, int]
Match = NamedTuple("Match", [('ref', Range), ('sig', Optional[Range])])


def get_range_list(start: int, end: int, length: int, step: int) -> List[Range]:
    return [(i, min(i + length, end)) for i in range(start, end, step)]


def base_synchronizer(reference: Iterable,
                      signal: Iterable,
                      match: Callable[[Iterable, Iterable], Iterable[Match]] = None,
                      accept: Callable[[Iterable[Match]], bool] = None) -> List[Match]:
    matches = match(reference, signal)
    if accept(matches):
        return matches
    else:
        # TODO add length of reference
        raise SynchronizationError('Could not synchronize reference ranges')
