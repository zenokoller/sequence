from typing import List
from unittest import TestCase

from utils.as_bytes import as_bytes


def feed_symbols_and_return_results(symbols: List[int]) -> List[int]:
    def feed(_symbols: List[int]):
        as_bytes_coro = as_bytes()
        for symbol in _symbols:
            yield as_bytes_coro.send(symbol)

    return [x for x in feed(symbols) if x is not None]


class TestAsBytes(TestCase):
    def test_returns_correct_bytes(self):
        actual = feed_symbols_and_return_results([3, 1, 2, 0, 3, 2, 0, 1])
        expected = [0xd8, 0x63, 0x8e, 0x38, 0xe1]
        self.assertEqual(expected, actual, 'Bytes not returned as expected.')

    def test_does_not_return_first_four(self):
        actual = feed_symbols_and_return_results([3, 1, 2, 0])
        expected = []
        self.assertEqual(expected, actual, 'Nothing should have been returned.')
