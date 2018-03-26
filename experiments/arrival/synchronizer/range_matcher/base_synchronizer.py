from typing import Callable, Tuple, List, Optional, Iterable

from synchronizer.exceptions import SynchronizationError
from synchronizer.range_matcher.match import Match

"""A synchronizer takes a signal and a reference and upon successful synchronization,
outputs a list of matches, where a match == (signal_offset, reference_offset)."""
Synchronizer = Callable[[Iterable, Iterable], Iterable[Match]]


def base_synchronizer(reference: Iterable,
                      signal: Iterable,
                      match: Callable[[Iterable, Iterable], Iterable[Match]] = None,
                      accept: Callable[[Iterable[Match]], bool] = None) -> List[Match]:
    matches = match(reference, signal)
    if accept(matches):
        return list(matches)
    else:
        raise SynchronizationError('Could not synchronize reference ranges')
