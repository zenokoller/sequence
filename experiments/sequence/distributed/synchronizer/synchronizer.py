import logging
from asyncio import Queue, ensure_future
from difflib import Match
from typing import Callable, List

from sequence.sequence import Sequence
from synchronizer.exceptions import SearchError
from synchronizer.search import full_search, recovery_search
from utils.symbol_buffer import SymbolBuffer


async def synchronize(seed: int, symbol_queue: Queue, event_queue: Queue, sequence_cls: Callable):
    state = Initial(sequence_cls(seed))
    while True:
        symbol = await symbol_queue.get()
        state, event = await state.next(symbol)
        if event is not None:
            await event_queue.put(event)
        # TODO: Can we use a decorator?


class State:
    __slots__ = 'sequence',

    async def next(self, symbol: int) -> 'State':
        raise NotImplementedError


INITIAL_SYNCH_CONFIDENCE = 10


class Initial(State):
    __slots__ = 'matched_count'

    def __init__(self, sequence: Sequence):
        self.sequence = sequence
        self.matched_count = 0

    async def next(self, symbol: int) -> State:
        expected, _ = next(self.sequence)
        if symbol == expected:
            self.matched_count += 1
            return Synchronized(
                self.sequence) if self.matched_count > INITIAL_SYNCH_CONFIDENCE else self
        else:
            return Searching.from_initial(self.sequence)


class Synchronized(State):
    def __init__(self, sequence: Sequence):
        logging.info(f'Synchronized at {sequence.offset}')
        self.sequence = sequence

    async def next(self, symbol: int) -> State:
        expected, _ = next(self.sequence)
        if symbol == expected:
            return self
        else:
            return Recovery.from_synchronized(symbol, self.sequence)


class AbstractSearchingState(State):
    __slots__ = 'buffer', 'out_queue', 'search_task'

    def __init__(self, sequence: Sequence, buffer: SymbolBuffer, search_fn: Callable,
                 search_args: dict = {}):
        self.sequence = sequence
        self.buffer = buffer
        self.out_queue = Queue()
        self.search_task = ensure_future(
            search_fn(self.out_queue, sequence=self.sequence, **search_args))

    async def next(self, symbol: int) -> State:
        self.buffer.append(symbol)
        if self.buffer.batch_full:
            await self.out_queue.put(self.buffer.batch)
        if self.search_task.done():
            return self.handle_search_done()
        else:
            return self

    @property
    def partial_batch_matches_sequence(self) -> bool:
        return all(
            symbol == expected for symbol, (expected, _) in zip(self.buffer.batch, self.sequence))

    def handle_search_done(self):
        raise NotImplementedError


RECOVERY_BATCH_SIZE = 25
RECOVERY_RANGE_LENGTH = 50


class Recovery(AbstractSearchingState):
    @classmethod
    def from_synchronized(cls, first_symbol: int, sequence: Sequence):
        logging.info('Synchronized -> Recovery')
        buffer = SymbolBuffer(batch_size=RECOVERY_BATCH_SIZE)
        buffer.append(first_symbol)
        search_args = {'range_': (sequence.offset, sequence.offset + RECOVERY_RANGE_LENGTH)}
        return cls(sequence, buffer, recovery_search, search_args=search_args)

    def handle_search_done(self) -> State:
        try:
            found_offset, matches = self.search_task.result()
        except SearchError:
            return Searching.from_recovery(self.sequence, self.buffer)

        self.sequence.set_offset(found_offset)
        if self.partial_batch_matches_sequence:
            return Synchronized(self.sequence)
        else:
            return Searching.from_recovery(self.sequence, self.buffer, prev_matches=matches)


SEARCHING_BATCH_SIZE = 50


class Searching(AbstractSearchingState):
    @classmethod
    def from_initial(cls, sequence: Sequence):
        logging.info('Initial -> Searching')
        return cls(sequence, SymbolBuffer(SEARCHING_BATCH_SIZE), full_search)

    @classmethod
    def from_recovery(cls, sequence: Sequence, prev_buffer: SymbolBuffer,
                      prev_matches: List[Match] = None):
        logging.info('Recovery -> Searching')
        prev_buffer = SymbolBuffer.from_previous(prev_buffer, SEARCHING_BATCH_SIZE)
        return cls(sequence, prev_buffer, full_search, search_args={'prev_matches': prev_matches})

    @classmethod
    def from_searching(cls, sequence: Sequence, prev_buffer: SymbolBuffer,
                       prev_matches: List[Match] = None):
        logging.info('Searching -> Searching')
        return cls(sequence, prev_buffer, full_search, search_args={'prev_matches': prev_matches})

    def handle_search_done(self) -> State:
        found_offset, matches = self.search_task.result()
        self.sequence.set_offset(found_offset)
        if self.partial_batch_matches_sequence:
            return Synchronized(self.sequence)
        else:
            return Searching.from_searching(self.sequence, self.buffer, prev_matches=matches)
