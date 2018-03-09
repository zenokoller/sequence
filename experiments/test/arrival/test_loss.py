from functools import partial
from unittest import TestCase

from simulator import simulator
from simulator.loss import ar1_loss
from utils.consume import consume_all

lose_all = partial(ar1_loss, prob=1)
keep_all = partial(ar1_loss, prob=0)
ar1_uncorrelated = partial(ar1_loss, prob=0.1, seed=38)
ar1_correlated = partial(ar1_loss, prob=0.5, corr=0.25, seed=38)

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

    def test_ar1_uncorrelated(self):
        expected = [0, 1, 2, 4, 5, 6, 7, 8, 9]
        actual = consume_all(simulator(test_sequence, [ar1_uncorrelated]))
        self.assertEqual(expected, actual, 'Actual items do not match expected items.')

    def test_ar1_correlated(self):
        expected = [0, 2, 4, 6]
        actual = consume_all(simulator(test_sequence, [ar1_correlated]))
        self.assertEqual(expected, actual, 'Actual items do not match expected items.')

