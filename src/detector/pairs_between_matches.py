from array import array
from difflib import SequenceMatcher, Match
from itertools import chain
from typing import Iterable, List

from detector.types import ActualExpected, Symbols
from sequence.sequence import Sequence
from synchronizer.sync_event import SyncEvent
from utils.iteration import pairwise


def pairs_between_matches(sync_event: SyncEvent, sequence: Sequence) -> Iterable[ActualExpected]:
    """Compares `sync_event`'s buffer to the appropriate part of the `sequence` to obtain
    matching blocks; returns the pieces between the matches along with their respective offsets."""
    lost_offset, found_offset, buffer = sync_event

    expected = sequence[lost_offset:found_offset]
    matches = get_matching_blocks(sync_event.buffer.array, expected)

    actual_indices = chain.from_iterable(
        [[0], *((m.a, m.a + m.size) for m in matches), [len(buffer)]])
    expected_indices = chain.from_iterable(
        [[0], *((m.b, m.b + m.size) for m in matches), [len(expected)]])

    actual = (
        Symbols(buffer[i:j], lost_offset + i) for i, j in pairwise(actual_indices))
    expected = (
        Symbols(sequence[i:j], lost_offset + i) for i, j in pairwise(expected_indices))
    return (ActualExpected(act, exp) for act, exp in zip(actual, expected)
            if not len(act.symbols) == len(exp.symbols) == 0)


def get_matching_blocks(actual: array, expected: array) -> List[Match]:
    sequence_matcher = SequenceMatcher()
    sequence_matcher.set_seqs(actual, expected)
    return sequence_matcher.get_matching_blocks()
