from random import Random
from typing import Iterable, Callable


def generate_sequence(get_next_bits: Callable[[int], int],
                      chunk_size: int,
                      offset: int = None) -> Iterable[int]:
    if offset is not None:
        get_next_bits(offset)
    while True:
        yield get_next_bits(chunk_size)


def generate_random_sequence(chunk_size: int,
                             offset: int = None,
                             seed: int = None) -> Iterable[int]:
    r = Random(seed)
    return generate_sequence(lambda k: r.getrandbits(k), chunk_size, offset=offset)

# Generate a sequence:
#   gen = generate_random_sequence(8, seed=42)
#   print([next(gen) for _ in range(10)])
