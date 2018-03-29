from typing import Tuple


def tuple_to_range(tup: Tuple[int, int]) -> range:
    return range(tup[0], tup[1])
