from functools import partial
from typing import Iterable, Callable, List, Tuple

from synchronizer.range_matcher.base_synchronizer import base_synchronizer
from signal_utils import consume_all
from synchronizer.range_matcher.base_synchronizer import Synchronizer
from synchronizer.range_matcher.match import Match
from synchronizer.range_matcher.range import get_range_list


def match_ranges_and_fill_gaps(reference: Iterable,
                               signal: Iterable,
                               n: int) -> List[Match]:
    return fill_gaps(match_ranges(reference, signal, n))


def match_ranges(reference: Iterable,
                 signal: Iterable,
                 n: int) -> List[Match]:
    """Splits `reference` into ranges of length n and tries to find their exact offsets in
    the `signal`. If none is found, the reference range is set to `None`"""
    reference, signal = (consume_all(x) for x in (reference, signal))

    sig_ranges = get_range_list(0, len(signal), n, 1)
    ref_ranges = get_range_list(0, len(reference), n, n)

    def find_match(r: Tuple[int, int]) -> Match:
        return Match(ref=r,
                     sig=next((s for s in sig_ranges
                               if signal[s[0]:s[1]] == reference[r[0]:r[1]]), None))

    return [find_match(ref_range) for ref_range in ref_ranges]


def fill_gaps(matches: List[Match]) -> List[Match]:
    """Assigns subsequent unmatched reference ranges to unmatched ranges in the signal."""
    coalesced = list(_merger(matches,
                             cond=lambda x: x.sig is None,
                             merge=lambda l: Match(ref=(l[0].ref[0], l[-1].ref[1]), sig=None)))

    def fill_gap(prev: Match, curr: Match, next_: Match) -> Match:
        if curr.sig is not None:
            return curr
        if prev is None:
            return Match(ref=curr.ref, sig=(0, next_.sig[0]))
        elif next_ is None:
            return Match(ref=curr.ref, sig=(prev.sig[1], -1))
        else:
            return Match(ref=curr.ref, sig=(prev.sig[1], next_.sig[0]))

    coalesced = [None] + coalesced + [None]
    return [fill_gap(*triplet) for triplet in zip(coalesced[0:-2], coalesced[1:-1], coalesced[2:])]


def _merger(iterable: Iterable, cond: Callable, merge: Callable) -> Iterable:
    it = iter(iterable)
    to_be_merged = []
    for item in it:
        if cond(item):
            to_be_merged.append(item)
        elif len(to_be_merged) > 0:
            yield merge(to_be_merged)
            to_be_merged = []
            yield item
        else:
            yield item


def accept(matches: List[Match], n: int) -> bool:
    """Check whether the matches make sense. The detected ones should not overlap and the gaps
    should not be too big."""
    have_matches = len(matches) > 0
    ascending_non_overlapping = all(m1.sig[0] < m2.sig[0] and m1.sig[1] <= m2.sig[0]
                                    for m1, m2 in zip(matches[:-1], matches[1:]))
    no_big_gaps = all(match.ref[1] - match.ref[0] <= 2 * n for match in matches)
    return have_matches and ascending_non_overlapping and no_big_gaps


def get_range_matcher(n: int) -> Synchronizer:
    return partial(base_synchronizer,
                   match=partial(match_ranges_and_fill_gaps, n=n),
                   accept=partial(accept, n=n))
