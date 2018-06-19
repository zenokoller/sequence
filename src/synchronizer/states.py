import logging
from asyncio import Queue, ensure_future
from typing import Callable, Tuple, Optional, Type

from sequence.sequence import Sequence
from synchronizer.exceptions import SearchError
from synchronizer.search import recovery_search, full_search
from synchronizer.sync_event import SyncEvent
from utils.symbol_buffer import SymbolBuffer

StateWithEvent = Tuple['State', Optional[SyncEvent]]


class State:
    __slots__ = 'sequence',

    async def next(self, symbol: int) -> StateWithEvent:
        raise NotImplementedError


def configure_states(initial_sync_confidence: int = None,
                     recovery_batch_size: int = None,
                     recovery_range_length: int = None,
                     recovery_min_match_size: int = None,
                     recovery_backoff_thresh: int = None,
                     searching_batch_size: int = None,
                     searching_min_match_size: int = None,
                     searching_backoff_thresh: int = None) -> Type[State]:
    """
    Configure the synchronizer's state machine states with the provided parameters.
    :param initial_sync_confidence correct symbols needed for move from `initial` to `synchronized`
    :param recovery_batch_size packets are buffered until search attempt is started in `recovery`
    :param recovery_range_length: how far to search forward from lost offset in recovery state
    :param recovery_min_match_size: minimum number of symbols for a successful sync in `recovery`
    :param recovery_backoff_thresh failed search attempts needed for move `recovery` -> `searching`
    :param searching_batch_size packets are buffered until search attempt is started in `searching`
    :param searching_min_match_size: minimum number of symbols for a successful sync in `searching`
    :param searching_backoff_thresh failed search attempts needed to declare failure
    :return: The initial state of the state machine
    """

    class Initial(State):
        __slots__ = 'matched_count'

        def __init__(self, sequence: Sequence):
            self.sequence = sequence
            self.matched_count = 0

        async def next(self, symbol: int) -> StateWithEvent:
            expected, _ = next(self.sequence)
            if symbol == expected:
                self.matched_count += 1
                next_state = Synchronized(
                    self.sequence) if self.matched_count > initial_sync_confidence else self
            else:
                next_state = Searching.from_initial(self.sequence)
            return next_state, None

    class Synchronized(State):
        def __init__(self, sequence: Sequence):
            logging.info(f'Synchronized at {sequence.offset}')
            self.sequence = sequence

        async def next(self, symbol: int) -> StateWithEvent:
            expected, _ = next(self.sequence)
            if symbol == expected:
                next_state = self
            else:
                next_state = Recovery.from_synchronized(symbol, self.sequence)
            return next_state, None

    class AbstractSearchingState(State):
        __slots__ = 'buffer', 'out_queue', 'search_task', 'lost_offset'

        def __init__(self, sequence: Sequence, buffer: SymbolBuffer, search_fn: Callable,
                     search_args: dict = None, lost_offset: int = None):
            self.sequence = sequence
            self.buffer = buffer
            self.lost_offset = lost_offset
            self.out_queue = Queue()
            self.search_task = ensure_future(
                search_fn(self.out_queue, sequence=self.sequence, **(search_args or {})))

        async def next(self, symbol: int) -> StateWithEvent:
            self.buffer.append(symbol)
            if self.buffer.batch_full:
                await self.out_queue.put(self.buffer.batch)
            if self.search_task.done():
                return self.handle_search_done()
            else:
                return self, None

        def get_sync_event(self, found_offset: int) -> SyncEvent:
            """Returns None if lost_offset is None (initial synch acquisition)"""
            return SyncEvent(self.lost_offset, found_offset, self.buffer) if \
                self.lost_offset is not None else None

        @property
        def partial_batch_matches_sequence(self) -> bool:
            return all(
                symbol == expected for symbol, (expected, _) in
                zip(self.buffer.batch, self.sequence))

        def handle_search_done(self):
            raise NotImplementedError

    class Recovery(AbstractSearchingState):
        @classmethod
        def from_synchronized(cls, first_symbol: int, sequence: Sequence):
            logging.info(f'Synchronized -> Recovery at {sequence.offset}')
            buffer = SymbolBuffer(batch_size=recovery_batch_size)
            buffer.append(first_symbol)
            search_args = {
                'min_match_size': recovery_min_match_size,
                'search_range': (sequence.offset, sequence.offset + recovery_range_length),
                'backoff_thresh': recovery_backoff_thresh
            }
            return cls(sequence, buffer, recovery_search, search_args=search_args,
                       lost_offset=sequence.offset - 1)

        def handle_search_done(self) -> StateWithEvent:
            try:
                found_offset = self.search_task.result()
            except SearchError:
                return Searching.from_recovery(self), None

            self.sequence.set_offset(found_offset)
            if self.partial_batch_matches_sequence:
                return Synchronized(self.sequence), self.get_sync_event(found_offset)
            else:
                return Searching.from_recovery(self), None

    class Searching(AbstractSearchingState):
        _search_args = {
            'min_match_size': searching_min_match_size,
            'backoff_thresh': searching_backoff_thresh
        }

        @classmethod
        def from_initial(cls, sequence: Sequence):
            logging.info('Initial -> Searching')
            return cls(sequence, SymbolBuffer(searching_batch_size), full_search,
                       search_args=cls._search_args, lost_offset=None)

        @classmethod
        def from_recovery(cls, state: Recovery):
            logging.info('Recovery -> Searching')
            buffer = SymbolBuffer.from_previous(state.buffer, searching_batch_size)
            return cls(state.sequence, buffer, full_search, search_args=cls._search_args,
                       lost_offset=state.lost_offset)

        @classmethod
        def from_searching(cls, state: 'Searching'):
            logging.info('Searching -> Searching')
            return cls(state.sequence, state.buffer, full_search, search_args=cls._search_args,
                       lost_offset=state.lost_offset)

        def handle_search_done(self) -> StateWithEvent:
            found_offset = self.search_task.result()
            self.sequence.set_offset(found_offset)
            if self.partial_batch_matches_sequence:
                return Synchronized(self.sequence), self.get_sync_event(found_offset)
            else:
                return Searching.from_searching(self), None

    return Initial
