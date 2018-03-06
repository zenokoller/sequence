# Given
#   - generator function (e.g. PI or PRG),
#   - seed (e.g.  IP address) and offset), -> argument of the sequence
#   - offset,
#   - n (bits in chunks)
# `generator` generates a predictable pseudorandom sequence that we can query
# with an iterable that yields n bit chunks.

# Hint: Use partial application to get generate_pi!
from typing import Iterable

Sequence = Iterable[int]  # TODO: should be a stream of bits


def counter() -> Iterable[int]:
    count = 0
    while True:
        yield count
        count += 1

# def chunk_by_bits(sequence: Sequence, offset: int) -> Sequence:
