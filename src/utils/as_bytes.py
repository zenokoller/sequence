from functools import partial
from typing import Iterable

from utils.coroutine import coroutine


@coroutine
def as_n_grams(symbol_width: int, n: int) -> Iterable[int]:
    buffer = 0
    mask = 2 ** (n * symbol_width) - 1
    for _ in range(n):
        buffer = ((buffer << symbol_width) & mask) | (yield)
    while True:
        buffer = ((buffer << symbol_width) & mask) | (yield buffer)


as_bytes = partial(as_n_grams, 2, 4)
