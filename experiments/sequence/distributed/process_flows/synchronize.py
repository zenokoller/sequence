from collections import Callable
from functools import partial
from typing import NamedTuple, Coroutine

from process_flows.search import start_search
from sequence.sequence import Sequence, get_default_sequence
from utils.coroutine import coroutine


class State(NamedTuple):
    synced: bool
    sequence: Sequence
    search: Coroutine

    @classmethod
    def initial(cls, seed: str, get_sequence: Callable):
        return cls(synced=True, sequence=get_sequence(seed), search=None)

    @classmethod
    def lost_sync(cls, search: Coroutine):
        return cls(synced=False, sequence=None, search=search)

    @classmethod
    def acquired_sync(cls, seed: str, pos: int, get_sequence: Callable):
        return cls(synced=True, sequence=get_sequence(seed, offset=pos), search=None)


@coroutine
def synchronize(seed: str, get_sequence: Callable):
    state = State.initial(seed, get_sequence)
    while True:
        symbol = yield
        synced, sequence, search = state
        if not synced:
            search.send(symbol)
            found_pos = next(search)
            if found_pos is not None:
                state = State.acquired_sync(seed, found_pos, get_sequence)
        elif not sequence.matches_next(symbol):
            search = start_search(symbol)
            state = State.lost_sync(search)


default_synchronize = partial(synchronize, get_sequence=get_default_sequence)
