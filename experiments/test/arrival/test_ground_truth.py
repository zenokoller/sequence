from unittest import TestCase

from utils.ground_truth import count_losses, count_reorderings, count_duplicates

original = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
perturbed = [3, 1, 2, 5, 6, 6, 6, 7, 10, 9, 9]

expected_losses = 2
expected_duplicates = 3
expected_reorderings = 3


class TestGroundTruth(TestCase):
    def test_count_losses(self):
        actual_losses = count_losses(original, perturbed)
        self.assertEqual(expected_losses, actual_losses, 'Number of losses does not match!')

    def test_count_duplicates(self):
        actual_duplicates = count_duplicates(perturbed)
        self.assertEqual(expected_duplicates, actual_duplicates,
                         'Number of duplicates does not match!')

    def test_count_reorderings(self):
        actual_reorderings = count_reorderings(perturbed)
        self.assertEqual(expected_reorderings, actual_reorderings,
                         'Number of reorderings does not match!')
