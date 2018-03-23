from unittest import TestCase
from synchronizer.max_flow.find_events import find_losses, find_reorders, find_dupe_candidates

TEST_SIG = [2, 4, 5, 6, 3, 7, 8, 7, 9, 10, 11, 13, 15, 16, 14]
TEST_REF = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
TEST_ALIGNMENT = [1, 3, 4, 5, 2, 6, 7, None, 8, 9, 10, 12, 14, 15, 13]


class TestFindEvents(TestCase):
    def test_find_losses(self):
        expected = [11]  # Note that we cannot find head or tail losses!
        actual = find_losses(TEST_ALIGNMENT)
        self.assertEqual(expected, actual, 'Did not find the expected loss indices.')

    def test_find_reorders(self):
        expected = {2: 3, 13: 2}
        actual = find_reorders(TEST_ALIGNMENT)
        self.assertEqual(expected, actual, 'Did not find the expected reordering delays.')

    def test_find_dupe_candidates(self):
        expected = [7]
        actual = find_dupe_candidates(TEST_ALIGNMENT)
        self.assertEqual(expected, actual, 'Did not find the expected duplicate candidates.')
