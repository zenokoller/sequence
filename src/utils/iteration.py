from itertools import chain, repeat
from typing import Iterable


def pairwise(iterable: Iterable):
    """Returns two elements of `iterable` at a time"""
    it = iter(iterable)
    while True:
        yield next(it), next(it)


def as_batches(items: list, batch_size: int = 1):
    """Returns the `items` in batches of `batch_size`"""
    l = len(items)
    for index in range(0, l, batch_size):
        yield items[index:min(index + batch_size, l)]


def n_cycles(iterable: Iterable, n: int):
    """Returns the sequence elements n times"""
    return chain.from_iterable(repeat(tuple(iterable), n))
