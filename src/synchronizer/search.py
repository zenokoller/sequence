from asyncio import Queue
from difflib import Match, SequenceMatcher
from typing import Tuple, Callable, List

from sequence.sequence import Sequence
from synchronizer.exceptions import SearchError


async def search(queue: Queue,
                 min_match_size: int = None,
                 backoff_thresh: int = None,
                 sequence: Sequence = None,
                 search_range: Tuple[int, int] = None) -> Tuple[int]:
    non_matched_count = 0
    get_longest_match = get_longest_match_fn(sequence, search_range)

    while True:
        batch = await queue.get()
        match = get_longest_match(batch)
        if match.size < min_match_size:
            non_matched_count += 1
            if non_matched_count > backoff_thresh:
                raise SearchError('reached maximum number of search attempts')
        else:
            matched_at_end = match.a + match.size == len(batch)
            if matched_at_end and queue.empty():
                found_offset = match.b + match.size
                return found_offset


def get_longest_match_fn(sequence: Sequence,
                         search_range: Tuple[int, int]) -> Callable[[List[int]], Match]:
    seq2 = sequence.as_list(search_range)
    sequence_matcher = SequenceMatcher()
    sequence_matcher.set_seq2(seq2)  # SequenceMatcher caches information about the second sequence

    # Need to adapt offset if restricting search space
    lower = search_range[0] if search_range is not None else 0

    def get_longest_match(seq1: List[int]) -> Match:
        sequence_matcher.set_seq1(seq1)
        match = sequence_matcher.find_longest_match(0, len(seq1), 0, len(seq2))
        return Match(a=match.a, b=match.b + lower, size=match.size)

    return get_longest_match
