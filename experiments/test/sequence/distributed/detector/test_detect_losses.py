from array import array
from typing import List, Tuple
from unittest import TestCase

from detector.detect_events import detect_losses, DetectInput
from detector.event import Events, Loss


def get_detect_input(offset: int, actual: List[int], expected: List[int]) -> DetectInput:
    return offset, as_array(actual), as_array(expected)


def as_array(l: List[int]) -> array:
    return array('B', l)


class TestDetectLosses(TestCase):
    def run_test(self, input: DetectInput, expected_losses: List[Loss]):
        actual_events = detect_losses(*input)
        self.assertEqual(expected_losses, actual_events, f'Events not predicted as expected.')

    def test_loss(self):
        input = get_detect_input(134, [], [2])
        expected_losses = [Loss(134, 1)]
        self.run_test(input, expected_losses)

    def test_two_losses(self):
        input = get_detect_input(7235,
                                 [0, 2, 2, 1, 0, 3, 2, 1],
                                 [2, 0, 2, 2, 1, 0, 3, 2, 1, 2])
        expected_losses = [Loss(7235, 1), Loss(7244, 1)]
        self.run_test(input, expected_losses)

    def test_three_losses(self):
        input = get_detect_input(412,
                                 [0, 2, 2, 1, 3, 2, 1],
                                 [2, 0, 2, 2, 1, 0, 3, 2, 1, 2])
        expected_losses = [Loss(412, 1), Loss(417, 1), Loss(421, 1)]
        self.run_test(input, expected_losses)

    def test_burst_loss(self):
        # Losses at positions 0, 2, 3 and 9
        input = get_detect_input(3942,
                                 [1, 3, 1, 3, 2],
                                 [3, 1, 0, 0, 3, 1, 3, 2, 3])
        expected_losses = [Loss(3942, 1), Loss(3944, 2), Loss(3950, 1)]
        self.run_test(input, expected_losses)
