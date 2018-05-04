from array import array
from difflib import Match
from typing import List, Tuple
from unittest import TestCase

from detector.detector import sync_event_to_actual_expected
from sequence.sequence import DefaultSequence
from synchronizer.sync_event import SyncEvent
from utils.symbol_buffer import SymbolBuffer

test_sequence = DefaultSequence(2315)

TEST_BATCH_SIZE = 15


def get_test_symbol_buffer(received: List[int]) -> SymbolBuffer:
    return SymbolBuffer(batch_size=TEST_BATCH_SIZE,
                        typecode='B',
                        prev_array=array('B', received))


def as_array(l: List[int]) -> array:
    return array('B', l)


class TestSyncEventToActualExpected(TestCase):
    def run_test(self, sync_event: SyncEvent, actuals: List[List[int]],
                 expecteds: List[Tuple[int, List[int]]]):
        expected_pairs = [pair for pair in zip(actuals, expecteds)]
        actual_pairs = [(list(act), (off, list(exp))) for act, (off, exp)
                        in sync_event_to_actual_expected(sync_event, test_sequence)]

        def pairs_match(expected_pair, actual_pair) -> bool:
            return expected_pair == actual_pair

        same_number_of_pairs = len(expected_pairs) == len(actual_pairs)
        all_pairs_match = all(pairs_match(*pairs) for pairs in zip(expected_pairs, actual_pairs))

        self.assertTrue(same_number_of_pairs and all_pairs_match,
                        f'Not all pairs match: '
                        f'\n\texpected: {expected_pairs}\n\tactual: {actual_pairs}')

    def test_matches_at_start(self):
        offsets = (3, 20)
        buffer = get_test_symbol_buffer([3, 0, 1, 2, 1, 0, 3, 2, 2, 3, 1, 0, 2, 0, 0])
        matches = [Match(a=0, b=4, size=11)]
        sync_event = SyncEvent(offsets, buffer, matches)

        actuals = [[], [0, 2, 0, 0]]
        expecteds = [(3, [0]), (15, [0, 0, 2, 0, 0])]

        self.run_test(sync_event, actuals, expecteds)

    def test_matches_in_middle(self):
        offsets = (1, 20)
        buffer = get_test_symbol_buffer([1, 0, 0, 1, 2, 1, 0, 3, 2, 2, 3, 1, 0, 2, 0])
        matches = [Match(a=2, b=5, size=10)]
        sync_event = SyncEvent(offsets, buffer, matches)

        actuals = [[1, 0], [0, 2, 0]]
        expecteds = [(1, [2, 1, 0, 3]), (15, [0, 0, 2, 0, 0])]

        self.run_test(sync_event, actuals, expecteds)

    def test_matches_at_end(self):
        offsets = (2, 19)
        buffer = get_test_symbol_buffer([3, 0, 1, 2, 1, 0, 3, 2, 2, 3, 1, 0, 0, 2, 0])
        matches = [Match(a=0, b=4, size=15)]
        sync_event = SyncEvent(offsets, buffer, matches)

        actuals = [[]]
        expecteds = [(2, [1, 0])]

        self.run_test(sync_event, actuals, expecteds)

    reference = [3, 0, 1, 1, 2, 0, 0, 3, 1, 2, 0, 1, 3, 1, 0, 2, 0, 2]

    def test_two_batches(self):
        offsets = (1, 35)
        buffer = get_test_symbol_buffer(
            [1, 0, 3, 0, 1, 2, 1, 0, 3, 2, 2, 3, 1, 0, 2, 0, 0, 3, 0, 1, 1, 2, 0, 0, 3, 1, 2, 0, 1,
             3])
        matches = [Match(a=0, b=2, size=14), Match(a=2, b=22, size=13)]
        sync_event = SyncEvent(offsets, buffer, matches)

        actuals = [[], [2, 0, 0]]
        expecteds = [(1, [2]), (16, [0, 2, 0, 0, 3, 0])]

        self.run_test(sync_event, actuals, expecteds)
