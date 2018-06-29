import logging
from collections import deque
from typing import List

from detect_events.events import Reordering
from utils.iteration import partition
from detect_events.types import Symbol, Symbols

DEFAULT_MAX_SIZE = 50
DEFAULT_IS_FIFO = False


class MissingBuffer:
    __slots__ = 'max_reorder_dist', 'max_size', 'is_fifo', '_queue'

    def __init__(self,
                 max_reorder_dist: int,
                 max_size: int = DEFAULT_MAX_SIZE,
                 is_fifo: bool = DEFAULT_IS_FIFO):
        self.max_reorder_dist = max_reorder_dist
        self.max_size = max_size
        self.is_fifo = is_fifo
        self._queue = deque(maxlen=max_size)

    def append(self, item: Symbols, buf_offset: int):
        for index, symbol in enumerate(item.symbols):
            self._queue.append(Symbol(symbol, item.offset + index, buf_offset))

    def remove_timed_out(self, offset: int) -> List[int]:
        """Removes symbols where `offset - symbol_offset > max_reorder_dist` and returns their
        offsets."""
        remaining, timed_out = partition(lambda item: offset - item.seq_offset > self.max_reorder_dist,
                                         self._queue)
        self._queue = deque(remaining, maxlen=self.max_size)
        return [offset for _, offset, _ in timed_out]

    def remove_if_found(self, needle: Symbols) -> List[Reordering]:
        """Walks the buffer, removing symbols that match the ones in `needle`, returning their
        offsets and reordering amounts. Walk direction is determined by `is_fifo`."""
        found = []
        remaining = list(self._queue) if self.is_fifo else list(reversed(self._queue))
        for index, symbol in enumerate(needle.symbols):
            try:
                found_idx, item = next((idx, item) for idx, item in enumerate(remaining)
                                       if item.symbol == symbol)
            except StopIteration:
                continue
            del remaining[found_idx]
            logging.info(f'Reordering extent: {needle.offset - item.buf_offset + index}')
            found.append(Reordering(item.seq_offset, needle.offset - item.buf_offset + index))
        self._queue = deque(remaining, maxlen=self.max_size)
        return found
