from asyncio import Queue
from difflib import Match, SequenceMatcher
from functools import partial
from typing import Tuple, Callable, List

from sequence.sequence import Sequence
from synchronizer.exceptions import SearchError
from utils.as_bytes import as_bytes


async def search(queue: Queue,
                 min_match_size: int = None,
                 backoff_thresh: int = None,
                 sequence: Sequence = None,
                 preprocess: Callable = None,
                 search_range: Tuple[int, int] = None) -> Tuple[int]:
    non_matched_count = 0
    get_longest_match = get_longest_match_fn(sequence, preprocess, search_range)

    while True:
        batch = await queue.get()
        original_batch_length = len(batch)
        batch = apply_coroutine(batch, preprocess)
        match = get_longest_match(batch)
        if match.size < min_match_size:
            non_matched_count += 1
            if non_matched_count > backoff_thresh:
                raise SearchError('reached maximum number of search attempts')
        else:
            matched_at_end = match.a + match.size == original_batch_length
            if matched_at_end and queue.empty():
                found_offset = match.b + match.size
                return found_offset


def get_longest_match_fn(sequence: Sequence,
                         preprocess: Callable,
                         search_range: Tuple[int, int]) -> Callable[[List[int]], Match]:
    seq2 = sequence.as_list(search_range)
    original_seq2_len = len(seq2)
    seq2 = apply_coroutine(seq2, preprocess)
    sequence_matcher = SequenceMatcher()
    sequence_matcher.set_seq2(seq2)  # SequenceMatcher caches information about the second sequence

    lower = search_range[0] if search_range is not None else 0
    processing_offset = original_seq2_len - len(seq2)

    def adapt_match(match: Match) -> Match:
        return Match(a=match.a, b=match.b + lower, size=match.size + processing_offset)

    def get_longest_match(seq1: List[int]) -> Match:
        sequence_matcher.set_seq1(seq1)
        match = sequence_matcher.find_longest_match(0, len(seq1), 0, len(seq2))
        return adapt_match(match)

    return get_longest_match


def apply_coroutine(items: list, coroutine: Callable) -> list:
    if coroutine is None:
        return items
    cr = coroutine()
    return [res for res in (cr.send(item) for item in items) if res is not None]


full_search_backoff_thresh = 10
full_search = partial(search,
                      backoff_thresh=full_search_backoff_thresh,
                      preprocess=as_bytes)

recovery_backoff_thresh = 3
recovery_search = partial(search,
                          backoff_thresh=recovery_backoff_thresh,
                          preprocess=as_bytes)
