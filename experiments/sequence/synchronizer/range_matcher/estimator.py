from difflib import Differ
from typing import Callable, List, Iterable

from synchronizer.range_matcher.base_synchronizer import Match

"""The estimator takes a signal, a reference and a list of matches 
[(sig_range, ref_range)] and returns a list of reference indices of 
the estimated event."""
Estimator = Callable[[list, list, Iterable[Match]], List[int]]


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
