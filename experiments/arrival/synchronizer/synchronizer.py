from typing import Callable, Tuple, List, Optional, Iterable, NamedTuple

"""A synchronizer takes a signal and a reference and upon successful synchronization,
outputs a list of matches, where a match == (signal_offset, reference_offset)."""
Synchronizer = Callable[[Iterable, Iterable], Optional[List[Tuple[int, int]]]]

Range = Tuple[int, int]
Match = NamedTuple("Match", [('ref', Range), ('sig', Optional[Range])])


def get_range_list(start: int, end: int, length: int, step: int) -> List[Range]:
    return [(i, min(i + length, end)) for i in range(start, end, step)]
