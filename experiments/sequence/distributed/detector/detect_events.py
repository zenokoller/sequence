from array import array
from difflib import SequenceMatcher, Match
from itertools import chain
from typing import Tuple, List

from detector.event import Events, Loss

DetectInput = Tuple[int, array, array]


def detect_losses(offset: int, actual: array, expected: array) -> List[Loss]:
    if len(actual) == 0:
        return [Loss(offset, len(expected))]
    elif len(expected) == 0:
        # Here, reordering and duplicates would be handled
        return []
    else:
        return list(chain.from_iterable(
            detect_losses(off, act, exp) for off, act, exp
            in split_by_longest_match((offset, actual, expected))
        ))


def split_by_longest_match(input: DetectInput) -> List[DetectInput]:
    offset, actual, expected = input
    m = get_longest_match(actual, expected)
    pairs = [(offset, actual[:m.a], expected[:m.b]),
             (offset + m.b + m.size, actual[m.a + m.size:], expected[m.b + m.size:])]
    return [(off, act, exp) for (off, act, exp) in pairs if not len(act) == len(exp) == 0]


def get_longest_match(actual: array, expected: array) -> Match:
    sequence_matcher = SequenceMatcher()
    sequence_matcher.set_seqs(actual, expected)
    return sequence_matcher.find_longest_match(0, len(actual), 0, len(expected))


Missing = List[array]


def detect_events(offset: int, actual: array, expected: array, missing) -> Tuple[Events, Missing]:
    """Signature subject to change, need to add timing information for expected symbols. Here,
    we probably have to find matching parts first instead of a recursive apporoach as in the
    loss-only solution."""
    raise NotImplementedError
