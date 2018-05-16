from typing import NamedTuple, List, Match, Tuple

from utils.symbol_buffer import SymbolBuffer


class SyncEvent(NamedTuple):
    offsets: Tuple[int, int]  # (lost_offset, found_offset)
    buffer: SymbolBuffer
