from asyncio import Event
from typing import Iterable

from utils.nanotime import nanosecond_timestamp


def filter_last_n_seconds(seconds: int, events: Iterable[Event]) -> Iterable[Event]:
    cutoff = nanosecond_timestamp() - seconds * 1e09
    return (event for event in events if event.timestamp > cutoff)

