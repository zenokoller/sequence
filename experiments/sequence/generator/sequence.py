from random import Random
from typing import Iterable, Callable


def generate_sequence(get_next_bits: Callable[[int], int], symbol_bits: int) -> Iterable[int]:
    while True:
        yield get_next_bits(symbol_bits)


def generate_random_sequence(symbol_bits: int, seed: int = None) -> Iterable[int]:
    r = Random(seed)
    return generate_sequence(lambda k: r.getrandbits(k), symbol_bits)

# Generate a sequence:
#   gen = generate_random_sequence(8, seed=42)
#   print([next(gen) for _ in range(10)])
