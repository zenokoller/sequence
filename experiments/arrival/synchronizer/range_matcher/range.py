from typing import Tuple, List

Range = Tuple[int, int]


def get_range_list(start: int, end: int, length: int, step: int) -> List[Range]:
    return [(i, min(i + length, end)) for i in range(start, end, step)]
