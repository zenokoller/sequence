from unittest import TestCase

from synchronizer.range_matcher import get_range_matcher

from synchronizer.synchronizer import Match

match_ranges = get_range_matcher(4)


class TestRangeMatcher(TestCase):
    def test_returns_correct_ranges(self):
        signal = [1, 2, 3, 0, 2, 1, 2, 0, 2]
        reference = [1, 2, 3, 0, 2, 1, 2, 2, 2, 0, 2]

        expected_matches = [Match(sig=(0, 4), ref=(0, 4)),
                            Match(sig=(4, 6), ref=(4, 8)),
                            Match(sig=(6, 9), ref=(8, 11))]
        actual_matches = match_ranges(signal, reference)

        return self.assertEqual(expected_matches, actual_matches, "Did not return correct matches.")

    def test_rejects_switched_ranges(self):
        signal = [1, 2, 3, 0, 2, 1, 2, 0]
        reference = [2, 1, 2, 0, 1, 2, 3, 0]
        return self.assertEqual(None, match_ranges(signal, reference),
                                "Should have rejected matches.")

    def test_rejects_big_gaps(self):
        signal = [1, 2, 3, 0, 1, 2, 0, 2]
        reference = [1, 2, 3, 0, 2, 1, 2, 3, 0, 3, 2, 2, 1, 3, 2, 1, 1, 2, 0, 2]
        return self.assertEqual(None, match_ranges(signal, reference),
                                "Should have rejected matches.")
