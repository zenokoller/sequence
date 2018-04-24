from functools import partial
from typing import Coroutine, List, Callable

import numpy as np

from utils.as_bytes import as_bytes

DEFAULT_BUFFER_SIZE = 50
DEFAULT_DTYPE = np.uint8


class SymbolBuffer:
    def __init__(self,
                 size: int = DEFAULT_BUFFER_SIZE,
                 dtype: np.dtype = DEFAULT_DTYPE,
                 preprocess: Callable = None):
        self.is_full = False
        self.size = size
        self.pre_cr = preprocess() if preprocess is not None else None
        self._buffer = np.zeros(self.size, dtype=dtype)
        self._index = -1

    def append(self, symbol: int):
        if self.pre_cr is not None:
            symbol = self.pre_cr.send(symbol)
        if symbol is not None:
            self._index = (self._index + 1) % self.size
            i = self._index
            self._buffer[i] = symbol
            self.is_full = i == self.size - 1

    def as_list(self) -> List[int]:
        return self._buffer.tolist()

    def as_partial_list(self) -> List[int]:
        return self._buffer[:self._index].tolist()


ByteBuffer = partial(SymbolBuffer, preprocess=as_bytes)
