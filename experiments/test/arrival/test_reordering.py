from functools import partial
from unittest import TestCase

from simulator import simulator
from simulator.reordering import fixed_delay
from .utils import consume_all

uncorrelated_fixed_delay = partial(fixed_delay, delay=2, prob=0.2, seed=38)

test_sequence = [x for x in range(10)]


class TestReordering(TestCase):
    def test_fixed_delay(self):
        expected = [0, 1, 2, 4, 5, 3, 6, 8, 9, 7]
        actual = consume_all(simulator(test_sequence, [uncorrelated_fixed_delay]))
        self.assertEqual(expected, actual, 'Sequence should have been reordered as expected.')
