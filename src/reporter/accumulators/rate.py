from collections import deque
from functools import partial
from typing import Iterable

from detector.events import Loss, Event
from reporter.accumulators.filter_last_n import filter_last_n_seconds
from utils.coroutine import coroutine

DEFAULT_LAST_N_SECONDS = 5
DEFAULT_BUFFER_SIZE = 10 ** 4


@coroutine
def rate_accumulator(period: int,
                     last_n_seconds: int = DEFAULT_LAST_N_SECONDS,
                     buffer_size: int = DEFAULT_BUFFER_SIZE) -> dict:
    buffer = deque(maxlen=buffer_size)
    _loss_rate = partial(loss_rate, period)
    filter_relevant = partial(filter_last_n_seconds, last_n_seconds)
    while True:
        values = {'loss_rate': _loss_rate(filter_relevant(buffer))}
        event = yield values
        buffer.append(event)


def loss_rate(period: int, events: Iterable[Event]) -> float:
    events = iter(events)
    loss_count = 0
    first = last = next(events, None)
    for last in events:
        loss_count += 1 if isinstance(last, Loss) else 0
    if last is not None:
        packet_count = (last.offset - first.offset) % period
        return loss_count / packet_count if packet_count > 0 else 0.0
    else:
        return 0.0
