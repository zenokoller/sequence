from functools import partial
from unittest import TestCase

import itertools

from experiments.test.arrival.utils import consume_all
from simulator import simulator
from simulator.duplication import duplication

no_dupes = partial(duplication, prob=0, corr=0)
uncorrelated_dupes = partial(duplication, prob=0.1, seed=38)
correlated_dupes = partial(duplication, prob=0.5, corr=0.5, seed=1)
all_dupes = partial(duplication, prob=1, corr=0)

test_sequence = [1, 2, 3, 4, 5]


class TestDuplication(TestCase):
    def test_no_dupes(self):
        expected = test_sequence
        actual = consume_all(simulator(test_sequence, [no_dupes]))
        self.assertEqual(expected, actual, 'Sequence should not have been changed.')

    def test_uncorrelated(self):
        expected = [1, 2, 3, 4, 4, 5]
        actual = consume_all(simulator(test_sequence, [uncorrelated_dupes]))
        self.assertEqual(expected, actual, 'Sequences no not match.')

    def test_correlated(self):
        expected = [1, 1, 2, 2, 3, 4, 4, 5, 5]
        actual = consume_all(simulator(test_sequence, [correlated_dupes]))
        self.assertEqual(expected, actual, 'Sequences no not match.')

    def test_all_dupes(self):
        expected = consume_all(
            itertools.chain.from_iterable([item, item] for item in test_sequence))
        actual = consume_all(simulator(test_sequence, [all_dupes]))
        self.assertEqual(expected, actual, 'Sequence should have been duplicated.')
