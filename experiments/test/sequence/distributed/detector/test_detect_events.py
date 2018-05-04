from array import array
from typing import List, Tuple
from unittest import TestCase

from detector.detector import detect_events
from detector.events import Events


class TestDetectEvents(TestCase):
    def test_detect_with_expected_events(self, actual: List[int], expected: Tuple[int, List[int]],
                                         expected_events: Events, missing=None):
        actual_events = detect_events(array('B', actual),
                                      (expected[0], array('B', expected[1])),
                                      missing or [])
        self.assertEqual(expected_events, actual_events, f'Events not predicted as expected.')

    def test_loss(self):
        actual = []
        expected = (134, [2])
        events = Events.losses_at([134])
        self.test_detect_with_expected_events(actual, expected, events)

    def test_two_losses(self):
        actual = [0, 2, 2, 1, 0, 3, 2, 1]
        expected = (7235, [2, 0, 2, 2, 1, 0, 3, 2, 1, 2])
        events = Events.losses_at(7235, 7244)
        self.test_detect_with_expected_events(actual, expected, events)

    def test_three_losses(self):
        actual = [0, 2, 2, 1, 3, 2, 1]
        expected = (412, [2, 0, 2, 2, 1, 0, 3, 2, 1, 2])
        events = Events.losses_at([412, 417, 421])
        self.test_detect_with_expected_events(actual, expected, events)

    def test_burst_loss(self):
        # Losses at positions 0, 2, 3 and 9
        actual = [0, 3, 1, 3, 2]
        expected = (3942, [3, 0, 0, 0, 3, 1, 3, 2, 3])
        events = Events.losses_at([3942, 3944, 3945, 3951])
        self.test_detect_with_expected_events(actual, expected, events)

    def test_reordering(self):
        # TODO: Also use `missing`
        raise NotImplementedError

    def test_duplicate(self):
        raise NotImplementedError
