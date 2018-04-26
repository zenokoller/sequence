import logging
from asyncio import Queue
from difflib import Match, SequenceMatcher
from functools import partial
from typing import Tuple, Callable, List

from sequence.sequence import Sequence
from utils.as_bytes import as_bytes
from .exceptions import SearchError


async def search(queue: Queue,
                 previous_matches: List[Match] = None,
                 batch_size: int = None,
                 min_match_size: int = None,
                 backoff_thresh: int = None,
                 sequence: Sequence = None,
                 preprocess: Callable = None) -> Tuple[int, List[Match]]:
    matches = previous_matches or []
    non_matched_count = 0
    get_longest_match = get_longest_match_fn(sequence, preprocess)

    while True:
        batch = await queue.get()
        batch = apply_coroutine(batch, preprocess)
        match = get_longest_match(batch)
        logging.debug(f'search: Got {match}')
        if match.size < min_match_size:
            non_matched_count += 1
            if non_matched_count > backoff_thresh:
                logging.warning('search: Reached maximum number of search trials; aborting.')
                raise SearchError
        else:
            matches.append(match)
            matched_at_end = match.a + match.size == len(batch)
            if matched_at_end and queue.empty():
                return match.b + batch_size, matches


def get_longest_match_fn(sequence: Sequence,
                         preprocess: Callable) -> Callable[[List[int]], Match]:
    seq2 = sequence.as_list()
    seq2 = apply_coroutine(seq2, preprocess)
    sequence_matcher = SequenceMatcher()
    sequence_matcher.set_seq2(seq2)

    def get_longest_match(seq1: List[int]) -> Match:
        sequence_matcher.set_seq1(seq1)
        return sequence_matcher.find_longest_match(0, len(seq1), 0, len(seq2))

    return get_longest_match


def apply_coroutine(items: list, coroutine: Callable) -> list:
    if coroutine is None:
        return items
    cr = coroutine()
    return [res for res in (cr.send(item) for item in items) if res is not None]


DEFAULT_BATCH_SIZE = 50
DEFAULT_MIN_MATCH_SIZE = 20
DEFAULT_BACKOFF_THRESH = 10

default_search = partial(search,
                         batch_size=DEFAULT_BATCH_SIZE,
                         min_match_size=DEFAULT_MIN_MATCH_SIZE,
                         backoff_thresh=DEFAULT_BACKOFF_THRESH,
                         preprocess=as_bytes)
