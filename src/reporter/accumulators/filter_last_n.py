from asyncio import Event
from collections import deque
from typing import Iterable

from utils.nanotime import nanosecond_timestamp


def filter_last_n_seconds(n: int, events: Iterable[Event]) -> Iterable[Event]:
    cutoff = nanosecond_timestamp() - n * 1e09
    return (event for event in events if event.timestamp > cutoff)


def filter_last_n_packets(period: int, n: int, last_offset: int, events: deque) -> Iterable[Event]:
    return (event for event in events if (last_offset - event.offset) % period < n)
