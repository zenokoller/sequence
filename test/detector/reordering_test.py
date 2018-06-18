from array import array
from typing import List
from unittest import TestCase

from detector.detect_losses_and_reorderings import get_detect_losses_and_reorderings
from detector.events import Reordering, Event, Loss
from sequence.sequence import default_sequence_args, get_sequence_cls
from synchronizer.sync_event import SyncEvent
from utils.override_defaults import override_defaults
from utils.symbol_buffer import SymbolBuffer

test_sequence_cls = get_sequence_cls(**override_defaults(default_sequence_args, {'symbol_bits': 8}))
test_sequence = test_sequence_cls(seed=2142)

expected = [
    239, 242, 173, 246, 209, 158, 188, 46, 194, 27, 27, 185, 224, 16, 55, 43, 8, 198, 234, 136
]

# Test cases
swap = [  # Reordering(5, 1)
    239, 242, 173, 246, 209, 188, 158, 46, 194, 27, 27, 185, 224, 16, 55, 43, 8, 198, 234, 136
]
burst_reordering_0 = [  # Reordering(4, 5), Reordering(3, 11)
    239, 242, 173, 158, 188, 46, 194, 27, 209, 27, 185, 224, 16, 55, 246, 43, 8, 198, 234, 136
]
burst_reordering_1 = [  # Reordering(3, 5), Reordering(4, 11)
    239, 242, 173, 158, 188, 46, 194, 27, 246, 27, 185, 224, 16, 55, 209, 43, 8, 198, 234, 136
]
burst_reordering_2 = [  # Reordering(3, 5), Reordering(4, 6)
    239, 242, 173, 158, 188, 46, 194, 27, 246, 209, 27, 185, 224, 16, 55, 43, 8, 198, 234, 136
]
one_loss = [  # Loss(2, 20) - the tail loss causes detection of the first one!
    239, 242, 246, 209, 158, 188, 46, 194, 27, 27, 185, 224, 16, 55, 43, 8, 198, 234
]
loss_and_reordering = [  # Loss(1, 20), Loss(2, 20), Reordering(16, 3)
    239, 246, 209, 158, 188, 46, 194, 27, 27, 185, 224, 16, 55, 43, 198, 234, 136, 8
]
two_reorderings = [  # Reordering(2, 2), Reordering(6, 3)
    239, 242, 246, 209, 173, 158, 46, 194, 27, 188, 27, 185, 224, 16, 55, 43, 8, 198, 234, 136
]


def get_test_sync_event(lost_offset: int, found_offset: int, symbols: List[int]) -> SyncEvent:
    buffer = SymbolBuffer(50, prev_array=array('B', symbols))
    return SyncEvent(lost_offset, found_offset, buffer)


class ReorderingTest(TestCase):
    @classmethod
    def setUpClass(cls):
        assert list(test_sequence[:len(expected)]) == expected, \
            '`expected` does not match beginning of `test_sequence`'

    def _test(self, received_symbols: List[int], expected_events: List[Event]):
        sync_event = get_test_sync_event(0, len(expected), received_symbols)
        actual = list(self.detect_events(sync_event, test_sequence))
        print(f'Expected:{expected_events}')
        print(f'Actual:{actual}')
        self.assertTrue(all(exp == act for exp, act in zip(expected_events, actual)),
                        'Expected events do not match actual events!')

    def setUp(self):
        self.detect_events = get_detect_losses_and_reorderings(max_reorder_dist=12)

    def test_swap(self):
        self._test(swap, [Reordering(5, 1)])

    def test_detect_burst_reordering_0(self):
        self._test(burst_reordering_0, [Reordering(4, 5), Reordering(3, 11)])

    def test_detect_burst_reordering_1(self):
        self._test(burst_reordering_1, [Reordering(3, 5), Reordering(4, 11)])

    def test_detect_burst_reordering_2(self):
        self._test(burst_reordering_2, [Reordering(3, 5), Reordering(4, 6)])

    def test_detect_one_loss(self):
        self._test(one_loss, [Loss(2, 20)])

    def test_detect_loss_and_reordering(self):
        self._test(loss_and_reordering, [Loss(1, 20), Loss(2, 20), Reordering(16, 3)])

    def test_detect_two_reorderings(self):
        self._test(two_reorderings, [Reordering(2, 2), Reordering(6, 3)])
