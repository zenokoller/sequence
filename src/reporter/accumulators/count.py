from typing import Coroutine

from detector.events import Reordering, Loss, Event
from reporter.exceptions import ReporterError
from utils.coroutine import coroutine


@coroutine
def count_accumulator(period: int) -> Coroutine[dict, Event, None]:
    """Accumulates packet, loss and reordering counts _without_ relying on explicit `Receive`
    events. Instead uses the difference in the offset of subsequent packets."""
    packets, losses, reorderings, _last_offset = 0, 0, 0, 0
    while True:
        event = yield {'packets': packets, 'losses': losses, 'reorderings': reorderings}
        if isinstance(event, Loss):
            losses += 1
        elif isinstance(event, Reordering):
            reorderings += 1
        else:
            raise ReporterError(f'Unexpected event: {event}')
        packets += (event.offset - _last_offset) % period
        _last_offset = event.offset
