from typing import List, Iterable
from unittest import TestCase

from detector.events import Loss
from pattern.gilbert_counts import GilbertCounts

TEST_PERIOD = 2 ** 16


def make_losses(loss_offsets: Iterable[int]) -> Iterable[Loss]:
    found_offset = max(loss_offsets) + 10
    return (Loss(offset, found_offset) for offset in loss_offsets)


class TestGilbertCounts(TestCase):
    def _test_with_offsets(self, loss_offsets: List[int], expected: GilbertCounts):
        losses = make_losses(loss_offsets)
        actual = GilbertCounts.from_events(TEST_PERIOD, losses)
        self.assertEqual(expected, actual, f'Count not updated as expected.')

    def test_non_consecutive_losses(self):
        loss_offsets = [4, 12, 15]
        expected = GilbertCounts(11, 3, 0, 0, 0)
        self._test_with_offsets(loss_offsets, expected)

    def test_triple_burst(self):
        loss_offsets = [4, 5, 6]
        expected = GilbertCounts(2, 3, 2, 0, 1)
        self._test_with_offsets(loss_offsets, expected)

    def test_double_burst(self):
        loss_offsets = [1, 5, 6]
        expected = GilbertCounts(5, 3, 1, 0, 0)
        self._test_with_offsets(loss_offsets, expected)

    def test_101_burst(self):
        loss_offsets = [2, 6, 8]
        expected = GilbertCounts(6, 3, 0, 1, 0)
        self._test_with_offsets(loss_offsets, expected)

    def test_longer(self):
        loss_offsets = [2, 4, 5, 6, 8, 9, 12]
        expected = GilbertCounts(10, 7, 3, 2, 1)
        self._test_with_offsets(loss_offsets, expected)
