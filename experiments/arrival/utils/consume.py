from itertools import islice
from typing import Iterable


def consume(sequence: Iterable, length: int) -> list:
    return list(islice(sequence, length))


def consume_all(sequence: Iterable) -> list:
    return [item for item in sequence]
