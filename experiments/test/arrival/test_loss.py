from functools import partial
from unittest import TestCase

from simulator import simulator
from simulator.loss import loss
from .utils import consume_all

lose_all = partial(loss, prob=1)
keep_all = partial(loss, prob=0)
uncorrelated = partial(loss, prob=0.1, seed=38)
correlated = partial(loss, prob=0.5, corr=0.25, seed=38)

test_sequence = [x for x in range(10)]


class TestLoss(TestCase):
    def test_lose_all(self):
        expected = []
        actual = consume_all(simulator(test_sequence, [lose_all]))
        self.assertEqual(expected, actual, 'All items should have been dropped.')

    def test_keep_all(self):
        expected = test_sequence
        actual = consume_all(simulator(test_sequence, [keep_all]))
        self.assertEqual(expected, actual, 'All of the items should have been kept.')

    def test_uncorrelated(self):
        expected = [0, 1, 2, 4, 5, 6, 7, 8, 9]
        actual = consume_all(simulator(test_sequence, [uncorrelated]))
        self.assertEqual(expected, actual, 'Actual items do not match expected items.')

    def test_correlated(self):
        expected = [0, 2, 4, 6]
        actual = consume_all(simulator(test_sequence, [correlated]))
        self.assertEqual(expected, actual, 'Actual items do not match expected items.')

