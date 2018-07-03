from typing import NamedTuple

from utils.symbol_buffer import SymbolBuffer


class SyncEvent(NamedTuple):
    lost_offset: int
    found_offset: int
    buffer: SymbolBuffer


class LostSyncEvent(NamedTuple):
    lost_offset: int
