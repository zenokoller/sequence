import logging
from asyncio import Queue, ensure_future
from collections import Callable
from difflib import Match
from functools import partial
from typing import List

from sequence.sequence import DefaultSequence
from synchronizer.exceptions import SearchError
from synchronizer.search import default_search
from utils.symbol_buffer import SymbolBuffer


class Synchronizer:
    def __init__(self,
                 seed: int,
                 queue: Queue,
                 sequence_cls: Callable = None,
                 search: Callable = None,
                 buffer_cls: type = None):
        self.seed = seed
        self.searching = False
        self.sequence = sequence_cls(seed)
        self.in_queue = queue  # Symbols from the flow
        self.out_queue = None  # Full buffers passed to the search_task
        self.buffer_cls = buffer_cls
        self.buffer = None
        self.search = partial(search, sequence=self.sequence)
        self.search_task = None

    async def synchronize(self):
        while True:
            symbol = await self.in_queue.get()
            if self.searching:
                try:
                    await self.continue_search(symbol)
                except SearchError:
                    return
            elif not self.sequence.matches_next(symbol):
                self.start_search(first_symbol=symbol)

    def start_search(self, first_symbol: int = None, previous_matches: List[Match] = None):
        logging.info(f'start_search: offset={self.sequence.offset}, first_symbol='
                     f'{first_symbol}')
        self.searching = True
        self.out_queue = self.out_queue if self.out_queue is not None else Queue()
        self.buffer = self.buffer if self.buffer is not None else self.buffer_cls()
        if first_symbol is not None:
            self.buffer.append(first_symbol)
        self.search_task = ensure_future(self.search(self.out_queue, previous_matches))

    async def continue_search(self, symbol: int):
        batch_full = self.buffer.append(symbol)
        if batch_full:
            await self.out_queue.put(self.buffer.last_batch())
        if self.search_task.done():
            self.stop_search()

    def stop_search(self):
        found_offset, matches = self.search_task.result()
        self.sequence.set_offset(found_offset)
        logging.info(f'stop_search: found_offset={self.sequence.offset}')

        if self.sequence.matches_next_bunch(self.buffer.partial_batch()):
            self.searching = False
            self.search_task = False
            self.out_queue = None
            self.buffer = None
        else:
            logging.info(f'stop_search: restart search; offset={self.sequence.offset}')
            self.start_search(previous_matches=matches)


DefaultSynchronizer = partial(Synchronizer,
                              sequence_cls=DefaultSequence,
                              search=default_search,
                              buffer_cls=SymbolBuffer)
