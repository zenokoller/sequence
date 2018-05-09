from array import array
from functools import partial
from itertools import islice
from random import Random
from typing import Iterable, Callable, List, Tuple


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

    def __iter__(self):
        return self

    def __next__(self) -> Tuple[int, int]:
        """Returns next (symbol, offset) of the sequence, advancing the offset by 1."""
        prev_offset = self.offset
        self.offset = (self.offset + 1) % self.period
        return self._sequence[prev_offset], prev_offset

    def __getitem__(self, key):
        return self._sequence[key]

    def set_offset(self, offset: int):
        self.offset = offset % self.period

    def as_list(self, range: Tuple[int, int] = None) -> List[int]:
        if range is not None:
            i, j = range
            return list(self._sequence[i:j])
        else:
            return list(self._sequence)


def generate_random(symbol_bits: int, seed: int) -> Iterable[int]:
    r = Random(seed or 0)
    while True:
        yield r.getrandbits(symbol_bits)


DEFAULT_SYMBOL_BITS = 2
DEFAULT_PERIOD = 2 ** 16
DEFAULT_GENERATE_FN = 'random'
DEFAULT_TYPECODE = 'B'
generate_functions = {
    'random': generate_random
}


def get_sequence_cls(symbol_bits: int = DEFAULT_SYMBOL_BITS,
                     period: int = DEFAULT_PERIOD,
                     generate_fn: str = DEFAULT_GENERATE_FN,
                     typecode: str = DEFAULT_TYPECODE):
    generate_fn = generate_functions[generate_fn]
    return partial(Sequence,
                   period=period,
                   generate=partial(generate_fn, symbol_bits),
                   typecode=typecode)
