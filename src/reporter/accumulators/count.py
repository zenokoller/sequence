from typing import Coroutine

from detector.events import Reordering, Loss, Event, Receive
from reporter.exceptions import ReporterError
from utils.coroutine import coroutine


@coroutine
def count_accumulator(period: int) -> Coroutine[dict, Event, None]:
    """Accumulates packet, loss and reordering counts."""
    packets, losses, reorderings = 0, 0, 0
    while True:
        event = yield {'packets': packets, 'losses': losses, 'reorderings': reorderings}
        if isinstance(event, Receive):
            packets += 1
        elif isinstance(event, Loss):
            losses += 1
        elif isinstance(event, Reordering):
            reorderings += 1
        else:
            raise ReporterError(f'Unexpected event: {event}')
