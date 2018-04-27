import array
import logging
from typing import List, Callable, Optional

DEFAULT_BATCH_SIZE = 50
DEFAULT_TYPECODE = 'B'


class SymbolBuffer:
    """Stores up to `batch_size` symbols in `batch` and periodically flushes them into `buffer`."""
    __slots__ = ('batch_size', 'batch', 'buffer')

    def __init__(self,
                 batch_size: int = DEFAULT_BATCH_SIZE,
                 typecode: str = DEFAULT_TYPECODE):
        self.batch = []
        self.batch_size = batch_size
        self.buffer = array.array(typecode)

    def append(self, symbol: int):
        if self.batch_full:
            self.buffer.extend(self.batch)
            self.batch = [symbol]
        else:
            self.batch.append(symbol)

    @property
    def batch_full(self) -> bool:
        return len(self.batch) == self.batch_size
