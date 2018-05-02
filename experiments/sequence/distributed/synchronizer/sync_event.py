from typing import NamedTuple, List, Match

from utils.symbol_buffer import SymbolBuffer


class SyncEvent(NamedTuple):
    lost_offset: int
    buffer: SymbolBuffer
    matches: List[Match]
