from collections import OrderedDict
from typing import List, Tuple


def arrival_information(original: List[int], received: List[int]) -> Tuple[int, int, int]:
    """Returns the number of losses, duplicates and reorderings in `actual` compared to
    `expected`, assuming that the elements in `expected` are unique."""
    return (count_losses(original, received),
            count_duplicates(received),
            count_reorderings(received))


def count_losses(expected: List[int], received: List[int]) -> int:
    return len(set(expected) - set(received))


def count_duplicates(items: List[int]) -> int:
    return len(items) - len(set(items))


def count_reorderings(items: List[int]) -> int:
    """Returns the total number of reorderings in `items`. For a single item, the number of
    reorderings is the number of smaller items that occur after that item, _without_ duplicates."""
    unique_items = list(OrderedDict.fromkeys(items))
    return sum(sum(item > other for other in unique_items[i + 1:])
               for i, item in enumerate(unique_items))
