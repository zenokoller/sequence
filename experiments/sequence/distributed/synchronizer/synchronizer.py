from asyncio import Queue, ensure_future
from collections import Callable
from functools import partial

from sequence.sequence import DefaultSequence
from synchronizer.exceptions import SynchronizationError
from synchronizer.search import default_search
from utils.symbol_buffer import ByteBuffer


class Synchronizer:
    def __init__(self,
                 seed: int,
                 queue: Queue,
                 sequence_cls: Callable = None,
                 search: Callable = None,
                 buffer_cls: type = None):
        self.seed = seed
        self.searching = False
        self.sequence_cls = sequence_cls
        self.sequence = sequence_cls(seed)
        self.in_queue = queue  # Symbols from the flow
        self.out_queue = None  # Full buffers passed to the search_task
        self.buffer_cls = buffer_cls
        self.buffer = None
        self.search = search
        self.search_task = None

    async def synchronize(self):
        while True:
            symbol = await self.in_queue.get()
            if self.searching:
                await self.continue_search(symbol)
            elif not self.sequence.matches_next(symbol):
                self.start_search(symbol)

    def start_search(self, symbol: int):
        self.searching = True
        self.buffer = self.buffer_cls()
        self.buffer.add_next(symbol)
        self.out_queue = Queue()
        self.search_task = ensure_future(self.search(self.seed, self.out_queue))
        print(f'start_search: {self.sequence.pos}')

    async def continue_search(self, symbol: int):
        self.buffer.add_next(symbol)
        if self.buffer.is_full:
            await self.out_queue.put(self.buffer.as_list())
        if self.search_task.done():
            self.stop_search()

    def stop_search(self):
        try:
            new_pos, _ = self.search_task.result()
        except SynchronizationError:
            print('SynchronizationError, stopping synchronizer.')
            return
        self.sequence = self.sequence_cls(self.seed, offset=new_pos)

        if self.sequence.matches_next_bunch(self.buffer.as_partial_list()):
            self.searching = False
            self.search_task = False
        else:
            self.start_search(None)
        print(f'stop_search: {self.sequence.pos}')


DefaultSynchronizer = partial(Synchronizer,
                              sequence_cls=DefaultSequence,
                              search=default_search,
                              buffer_cls=ByteBuffer)
