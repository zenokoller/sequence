from array import array
from typing import NamedTuple, List, Match


class SyncEvent(NamedTuple):
    lost_index: int
    buffer: array
    matches: List[Match]
