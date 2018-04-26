import logging
from array import array
from functools import partial
from itertools import islice
from random import Random
from typing import Iterable, Callable, List


class Sequence:
    __slots__ = ('_sequence', 'offset', 'period')

    def __init__(self,
                 seed: int,
                 offset: int = None,
                 period: int = None,
                 generate: Callable[[int], Iterable[int]] = None,
                 typecode: str = None):
        self.period = period
        self.offset = offset or 0
        self._sequence = array(typecode, (x for x in islice(generate(seed), None, period)))

    def matches_next(self, symbol: int) -> bool:
        expected = self._sequence[self.offset]
        logging.debug(f'matches_next: ({self.offset}, {expected}, {symbol})')
        self.offset = (self.offset + 1) % self.period
        return symbol == expected

    def matches_next_bunch(self, symbols: List[int]) -> bool:
        prev_offset = self.offset
        self.offset = (self.offset + len(symbols)) % self.period
        logging.debug(f'matches_next_bunch: ([{prev_offset},{self.offset}], TBD add symbols...)')
        return all(symbol == expected for symbol, expected
                   in zip(symbols, self._sequence[prev_offset:self.offset + 1]))

    def set_offset(self, offset: int):
        self.offset = offset % self.period

    def as_list(self):
        return list(self._sequence)

    def __iter__(self):
        return self

    def __next__(self):
        self.offset = (self.offset + 1) % self.period
        return self._sequence[self.offset]


def generate_random(symbol_bits: int, seed: int) -> Iterable[int]:
    r = Random(seed or 0)
    while True:
        yield r.getrandbits(symbol_bits)


default_symbol_bits = 2
default_period = 2 ** 16
default_generate_sequence = partial(generate_random, default_symbol_bits)
DefaultSequence = partial(Sequence,
                          period=default_period,
                          generate=default_generate_sequence,
                          typecode='B')
