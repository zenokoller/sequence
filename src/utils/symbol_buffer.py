from array import array
from typing import Iterable

from utils.iteration import as_batches

DEFAULT_TYPECODE = 'B'


class SymbolBuffer:
    """Stores up to `batch_size` symbols in `batch` and periodically flushes them into `buffer`."""
    __slots__ = 'batch_size', 'batch', 'array'

    def __init__(self,
                 batch_size: int,
                 typecode: str = DEFAULT_TYPECODE,
                 prev_array: array = None):
        self.batch = []
        self.batch_size = batch_size
        self.array = prev_array or array(typecode)

    def __len__(self):
        return len(self.array)

    def __getitem__(self, key):
        return self.array[key]

    def append(self, symbol: int):
        if self.batch_full:
            self.array.extend(self.batch)
            self.batch = [symbol]
        else:
            self.batch.append(symbol)

    def as_batches(self) -> Iterable[array]:
        return as_batches(self.array, self.batch_size)

    @property
    def batch_full(self) -> bool:
        return len(self.batch) == self.batch_size

    @classmethod
    def from_previous(cls, buffer: 'SymbolBuffer', new_batch_size: int) -> 'SymbolBuffer':
        buffer.array.extend(buffer.batch)
        return cls(new_batch_size, buffer.array.typecode, buffer.array)
