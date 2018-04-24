from functools import partial
from itertools import islice
from random import Random
from typing import Iterable, Callable, List


class Sequence:
    __slots__ = ('it', 'pos', 'period')

    def __init__(self, seed: str, offset: int = None, period: int = None,
                 generate_sequence: Callable[[str], Iterable[int]] = None):
        gen = generate_sequence(seed)
        if offset is not None:
            gen = islice(gen, offset + 1, None)
            self.pos = offset
        else:
            self.pos = -1
        self.it = iter(gen)
        self.period = period

    def matches_next(self, symbol: int) -> bool:
        self.pos = (self.pos + 1) % self.period
        expected = next(self.it)
        return symbol == expected

    def matches_next_bunch(self, symbols: List[int]) -> bool:
        self.pos = (self.pos + len(symbols)) % self.period
        return all(symbol == expected for symbol, expected in zip(symbols, self.it))

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.it)


def generate_random_sequence(symbol_bits: int, period: int, seed: str) -> Iterable[int]:
    while True:
        r = Random(seed or 0)
        counter = 0
        while counter < period:
            counter += 1
            yield r.getrandbits(symbol_bits)


default_symbol_bits = 2
default_period = 2 ** 16
default_generate_sequence = partial(generate_random_sequence, default_symbol_bits, default_period)
DefaultSequence = partial(Sequence,
                          period=default_period,
                          generate_sequence=default_generate_sequence)
