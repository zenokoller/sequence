import logging
from asyncio import Queue, ensure_future
from difflib import Match
from typing import Callable, List, Optional, Tuple

from sequence.sequence import Sequence
from synchronizer.exceptions import SearchError
from synchronizer.search import full_search, recovery_search
from synchronizer.sync_event import SyncEvent
from utils.symbol_buffer import SymbolBuffer


async def synchronize(seed: int, symbol_queue: Queue, event_queue: Queue, sequence_cls: Callable):
    state = Initial(sequence_cls(seed))
    while True:
        symbol = await symbol_queue.get()
        state, event = await state.next(symbol)
        if event is not None:
            await event_queue.put(event)


StateWithEvent = Tuple['State', Optional[SyncEvent]]


class State:
    __slots__ = 'sequence',

    async def next(self, symbol: int) -> StateWithEvent:
        raise NotImplementedError


INITIAL_SYNCH_CONFIDENCE = 10


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
                self.sequence) if self.matched_count > INITIAL_SYNCH_CONFIDENCE else self
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

    def __init__(self, sequence: Sequence, buffer: SymbolBuffer,
                 search_fn: Callable, search_args: dict = None, lost_offset: int = None):
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

    def get_sync_event(self, found_offset: int, matches: List[Match]) -> SyncEvent:
        """Returns None if lost_offset is None (initial synch acquisition)"""
        return SyncEvent((self.lost_offset, found_offset), self.buffer, matches) if \
            self.lost_offset is not None else None

    @property
    def partial_batch_matches_sequence(self) -> bool:
        return all(
            symbol == expected for symbol, (expected, _) in zip(self.buffer.batch, self.sequence))

    def handle_search_done(self):
        raise NotImplementedError


RECOVERY_BATCH_SIZE = 25
RECOVERY_RANGE_LENGTH = 75


class Recovery(AbstractSearchingState):
    @classmethod
    def from_synchronized(cls, first_symbol: int, sequence: Sequence):
        logging.info(f'Synchronized -> Recovery at {sequence.offset}')
        buffer = SymbolBuffer(batch_size=RECOVERY_BATCH_SIZE)
        buffer.append(first_symbol)
        search_args = {'range_': (sequence.offset, sequence.offset + RECOVERY_RANGE_LENGTH)}
        return cls(sequence, buffer, recovery_search, search_args=search_args,
                   lost_offset=sequence.offset - 1)

    def handle_search_done(self) -> StateWithEvent:
        try:
            found_offset, matches = self.search_task.result()
        except SearchError:
            return Searching.from_recovery(self), None

        self.sequence.set_offset(found_offset)
        if self.partial_batch_matches_sequence:
            return Synchronized(self.sequence), self.get_sync_event(found_offset, matches)
        else:
            return Searching.from_recovery(self, prev_matches=matches), None


SEARCHING_BATCH_SIZE = 50


class Searching(AbstractSearchingState):
    @classmethod
    def from_initial(cls, sequence: Sequence):
        logging.info('Initial -> Searching')
        return cls(sequence, SymbolBuffer(SEARCHING_BATCH_SIZE), full_search, lost_offset=None)

    @classmethod
    def from_recovery(cls, state: Recovery, prev_matches: List[Match] = None):
        logging.info('Recovery -> Searching')
        buffer = SymbolBuffer.from_previous(state.buffer, SEARCHING_BATCH_SIZE)
        return cls(state.sequence, buffer, full_search, lost_offset=state.lost_offset,
                   search_args={'prev_matches': prev_matches})

    @classmethod
    def from_searching(cls, state: 'Searching', prev_matches: List[Match] = None):
        logging.info('Searching -> Searching')
        return cls(state.sequence, state.buffer, full_search, lost_offset=state.lost_offset,
                   search_args={'prev_matches': prev_matches})

    def handle_search_done(self) -> StateWithEvent:
        found_offset, matches = self.search_task.result()
        self.sequence.set_offset(found_offset)
        if self.partial_batch_matches_sequence:
            return Synchronized(self.sequence), self.get_sync_event(found_offset, matches)
        else:
            return Searching.from_searching(self, prev_matches=matches), None
