from asyncio import Queue
from difflib import Match, SequenceMatcher
from functools import partial
from typing import Tuple, Callable, Coroutine, List

from sequence.sequence import Sequence
from utils.as_bytes import as_bytes
from .exceptions import SynchronizationError


async def search(queue: Queue,
                 previous_matches: List[Match] = None,
                 batch_size: int = None,
                 min_match_size: int = None,
                 backoff_thresh: int = None,
                 sequence: Sequence = None,
                 preprocess: Coroutine = None) -> Tuple[int, List[Match]]:
    matches = previous_matches or []
    non_matched_count = 0
    get_longest_match = get_longest_match_fn(batch_size, sequence, preprocess)

    while True:
        batch = await queue.get()
        match = get_longest_match(batch)
        if match.size < min_match_size:
            non_matched_count += 1
            if non_matched_count > backoff_thresh:
                raise SynchronizationError
            continue

        matches.append(match)
        matched_at_end = match.a + match.size == batch_size
        if matched_at_end and queue.empty():
            return match.b + batch_size, matches


def get_longest_match_fn(batch_size: int,
                         sequence: Sequence,
                         preprocess: Callable) -> Callable[[List[int]], Match]:
    seq2 = sequence.as_list()
    if preprocess is not None:
        pre_cr = preprocess()
        seq2 = [pre_cr.send(symbol) for symbol in seq2]
    sequence_matcher = SequenceMatcher()
    sequence_matcher.set_seq2(seq2)

    def get_longest_match(batch: List[int]) -> Match:
        sequence_matcher.set_seq1(batch)
        return sequence_matcher.find_longest_match(0, batch_size, 0, len(seq2))

    return get_longest_match


DEFAULT_BATCH_SIZE = 50
DEFAULT_MIN_MATCH_SIZE = 20
DEFAULT_BACKOFF_THRESH = 10

default_search = partial(search,
                         batch_size=DEFAULT_BATCH_SIZE,
                         min_match_size=DEFAULT_MIN_MATCH_SIZE,
                         backoff_thresh=DEFAULT_BACKOFF_THRESH,
                         preprocess=as_bytes)
