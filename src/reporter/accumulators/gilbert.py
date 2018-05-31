from collections import deque
from functools import partial
from typing import Iterable

from detector.events import Event
from pattern.gilbert_counts import GilbertCounts
from reporter.accumulators.utils import filter_last_n_seconds
from utils.coroutine import coroutine

DEFAULT_LAST_N_SECONDS = 500
DEFAULT_BUFFER_SIZE = 10 ** 4


@coroutine
def gilbert_accumulator(period: int,
                        last_n_seconds: int = DEFAULT_LAST_N_SECONDS,
                        buffer_size: int = DEFAULT_BUFFER_SIZE) -> dict:
    buffer = deque(maxlen=buffer_size)
    _ge_params = partial(ge_params, period)
    filter_relevant = partial(filter_last_n_seconds, last_n_seconds)
    while True:
        values = _ge_params(filter_relevant(buffer))
        event = yield values
        buffer.append(event)


def ge_params(period: int, events: Iterable[Event]) -> dict:
    return GilbertCounts.from_events(period, events).to_params()


