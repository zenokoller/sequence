from functools import partial
from random import Random
from typing import Iterable


def generate_random_sequence(symbol_bits: int, period: int, seed: str) -> Iterable[
    int]:
    while True:
        r = Random(seed or 0)
        counter = 0
        while counter < period:
            counter += 1
            yield r.getrandbits(symbol_bits)


default_gen_sequence = partial(generate_random_sequence, 2, 2**16)
