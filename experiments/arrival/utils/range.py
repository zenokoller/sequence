from typing import Tuple, Iterable


def tuple_to_range(tup: Tuple[int, int]) -> range:
    return range(tup[0], tup[1])


def matching_ranges(first: Iterable[int],
                    second: Iterable[int]) -> Iterable[Tuple[int, int]]:
    """Given two lists `first` and `second`, yields bounds of matching subsequences."""
    start = None
    for i, (a, b) in enumerate(zip(first, second)):
        if a == b and start is None:
            start = i
        elif a != b and start is not None:
            yield (start, i)
            start = None

    if start is not None:
        yield (start, min(len(first), len(second)))
    return
