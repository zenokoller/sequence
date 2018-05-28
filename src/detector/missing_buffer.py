from collections import deque
from typing import List

from detector.types import Symbol, Delay, Symbols
from utils.iteration import partition

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

    def append(self, item: Symbols):
        for index, symbol in enumerate(item.symbols):
            self._queue.append(Symbol(symbol, item.offset + index))

    def remove_timed_out(self, offset: int) -> List[int]:
        """Removes symbols where `offset - symbol_offset > max_reorder_dist` and returns their
        offsets."""
        remaining, timed_out = partition(lambda item: offset - item.offset > self.max_reorder_dist,
                                         self._queue)
        self._queue = deque(remaining, maxlen=self.max_size)
        return [offset for _, offset in timed_out]

    def remove_if_found(self, needle: Symbols) -> List[Delay]:
        """Walks the buffer, removing symbols that match the ones in `needle`, returning their
        offsets and delays. Walk direction is determined by `is_fifo`."""
        found = []
        remaining = list(self._queue) if self.is_fifo else list(reversed(self._queue))
        for index, symbol in enumerate(needle.symbols):
            try:
                found_idx, item = next((idx, item) for idx, item in enumerate(remaining)
                                       if item.symbol == symbol)
            except StopIteration:
                continue
            del remaining[found_idx]
            found.append(Delay(item.offset, needle.offset - item.offset - index))
        self._queue = deque(remaining, maxlen=self.max_size)
        return found
