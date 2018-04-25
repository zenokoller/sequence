import array
from typing import List, Callable

DEFAULT_BATCH_SIZE = 50
DEFAULT_TYPECODE = 'B'


class SymbolBuffer:
    __slots__ = ('_batch_index', 'batch_size', '_buffer')

    def __init__(self,
                 batch_size: int = DEFAULT_BATCH_SIZE,
                 typecode: str = DEFAULT_TYPECODE):
        self._batch_index = 0
        self.batch_size = batch_size
        self._buffer = array.array(typecode)

    def append(self, symbol: int) -> bool:
        self._buffer.append(symbol)
        self._batch_index = (self._batch_index + 1) % self.batch_size
        return self._batch_index == 0

    def last_batch(self) -> List[int]:
        return list(self._buffer[-self._batch_index:])
