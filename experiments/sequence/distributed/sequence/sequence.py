from functools import partial
from itertools import islice
from random import Random
from typing import Iterable, Callable


class Sequence:
    __slots__ = ('it', 'pos')


def get_sequence_cls(generate_sequence: Callable[[str], Iterable[int]], period: int) -> Sequence:
    class _Sequence:
        __slots__ = ('it', 'pos')

        def __init__(self, seed: str, offset: int = None):
            gen = generate_sequence(seed)
            if offset is not None:
                gen = islice(gen, offset, None)
            self.it = iter(gen)
            self.pos = -1

        def matches_next(self, symbol: int) -> bool:
            self.pos = (self.pos + 1) % period
            expected = next(self.it)
            print(f'{self.pos}: expected {expected}, got {symbol}')
            return symbol == expected

        def __iter__(self):
            return self

        def __next__(self):
            return next(self.it)

    return _Sequence


def generate_random_sequence(symbol_bits: int, period: int, seed: str) -> Iterable[
    int]:
    while True:
        r = Random(seed or 0)
        counter = 0
        while counter < period:
            counter += 1
            yield r.getrandbits(symbol_bits)


default_symbol_bits = 2
default_period = 2 ** 16
default_generate_sequence = partial(generate_random_sequence, default_symbol_bits, default_period)
DefaultSequence = get_sequence_cls(default_generate_sequence, default_period)


def get_default_sequence(seed: str):
    return DefaultSequence(seed)
