from typing import Iterable
from unittest import TestCase

from simulator import simulator
from utils.consume import consume_all

test_sequence = [1, 2, 3, 4, 5]


class TestSimulator(TestCase):
    def test_empty_policy(self):
        expected = test_sequence
        actual = consume_all(simulator(test_sequence, []))
        self.assertEqual(expected, actual, 'Returned sequence should not have been altered.')

    def test_lose_every_second(self):
        def lose_every_second(sequence: Iterable) -> Iterable:
            it = iter(sequence)
            lose_item = False
            while True:
                try:
                    if lose_item:
                        next(it)
                    else:
                        yield next(it)
                    lose_item = not lose_item
                except StopIteration:
                    return

        expected = [1, 3, 5]
        actual = consume_all(simulator(test_sequence, [lose_every_second]))
        self.assertEqual(expected, actual, 'Every second element should be missing.')
