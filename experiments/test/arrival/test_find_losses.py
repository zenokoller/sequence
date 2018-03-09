from unittest import TestCase

from synchronizer.find_losses import find_losses

original = [1, 2, 3, 2, 2, 1, 2, 2, 0, 1, 2, 3, 0, 2, 1]
received = [1, 2, 3, 2, 1, 2, 2, 0, 1, 2, 2, 1]
expected_losses = [3, 11, 12]


class TestFindLosses(TestCase):
    def test_find_losses(self):
        actual_losses = find_losses(original, received)
        self.assertEqual(expected_losses, actual_losses, 'Found losses not match expected losses!')
