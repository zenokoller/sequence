from functools import partial
from itertools import accumulate
from typing import Iterable


def encode_integer(int_: int, length: int = None) -> bytes:
    return int_.to_bytes(length, byteorder='little')


def decode_integer(data) -> int:
    return int.from_bytes(data, byteorder='little')


def encode_integers(xs: Iterable[int], lengths: Iterable[int] = None) -> bytes:
    return b''.join((x.to_bytes(length, byteorder='little') for x, length in zip(xs, lengths)))


def decode_integers(data, lengths: Iterable[int] = None) -> tuple:
    acc = list(accumulate([0] + list(lengths)))
    return tuple(int.from_bytes(data[a:b], byteorder='little') for a, b in zip(acc[:-1], acc[1:]))


SYMBOL_LENGTH = 1
encode_symbol = partial(encode_integer, length=SYMBOL_LENGTH)
decode_symbol = decode_integer

SYMBOL_WITH_OFFSET_LENGTHS = (1, 4)
encode_symbol_with_offset = partial(encode_integers, lengths=SYMBOL_WITH_OFFSET_LENGTHS)
decode_symbol_with_offset = partial(decode_integers, lengths=SYMBOL_WITH_OFFSET_LENGTHS)
