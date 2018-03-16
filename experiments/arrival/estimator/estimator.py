from difflib import Differ
from itertools import chain
from typing import Callable, List, Iterable

from synchronizer.range_matcher import get_range_matcher
from synchronizer.synchronizer import Match

"""The estimator takes a signal, a reference and a list of matches 
[(sig_range, ref_range)] and returns a list of reference indices of 
the estimated event."""
Estimator = Callable[[list, list, List[Match]], List[int]]


def estimate_losses(reference: list, signal: list, matches: List[Match]) -> List[int]:
    return sum((_losses(reference, signal, match) for match in matches), [])


def _losses(reference: list, signal: list, match: Match) -> List[int]:
    diff = get_diff(reference[match.ref[0]:match.ref[1]],
                    signal[match.sig[0]:match.sig[1]])
    return [match.ref[0] + index for index, item in enumerate(diff) if item[0] == '-']


def get_diff(a: Iterable, b: Iterable) -> Iterable[str]:
    return Differ().compare(*(as_string(list_) for list_ in (a, b)))


def as_string(sequence: Iterable) -> str:
    return ''.join(str(el) for el in sequence)


match_ranges = get_range_matcher(4)

reference = [1, 2, 3, 0, 2, 1, 2, 2, 2, 0, 2]
signal = [1, 2, 3, 0, 2, 1, 2, 0, 2]

print(estimate_losses(reference, signal, match_ranges(reference, signal)))
