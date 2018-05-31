from collections import deque
from functools import partial
from typing import Iterable, NamedTuple

from detector.events import Event, Loss
from reporter.accumulators.utils import filter_last_n_seconds
from utils.coroutine import coroutine

DEFAULT_LAST_N_SECONDS = 500
DEFAULT_BUFFER_SIZE = 10 ** 4


@coroutine
def ge_accumulator(period: int,
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


class GilbertCounts(NamedTuple):
    packet: int = 0
    loss: int = 0
    burst_11: int = 0
    burst_101: int = 0
    burst_111: int = 0
    highest_seen_offset: int = 0

    @classmethod
    def from_events(cls, period: int, events: Iterable[Event]) -> 'GilbertCounts':
        """Approximates parameters of the Gilbert model from events by using counts of loss,
        double loss bursts, triple loss bursts and 1-0-1 loss bursts using method proposed in:

            Gilbert, E.N.: Capacity of a Burst-Noise Channel. Bell System Technical Journal 39

        TL;DR:
        assume error-free good state: k=1 (this is the Gilbert Model)
        maintain a = P(1), b = P(1|1), P(101), P(111)
        compute c = P(111) / (P(101) + P(111)), then derive params as
                1 - r = (a * c - b * b) / (2*a*c - b * (a + c))
                h = 1 - (b / (1 - r))
                p = a * r / (1 - h - a)
        """
        events = iter(events)
        update = partial(GilbertCounts._update, period)
        first_two = (next(events, None), next(events, None))
        counts = GilbertCounts._from_first_two_losses(period, *first_two)
        last_three = deque(maxlen=3)
        last_three.extend(first_two)
        for event in events:
            if not isinstance(event, Loss):
                continue
            last_three.append(event)
            counts = update(counts, last_three)
        return counts

    @classmethod
    def _from_first_two_losses(cls, period: int, first: Loss, second: Loss):
        if first is None:
            return GilbertCounts()
        elif second is None:
            return GilbertCounts(loss=1, highest_seen_offset=first.offset)
        else:
            return GilbertCounts(packet=(second.offset - first.offset) % period,
                                 loss=2,
                                 burst_11=(second.offset - first.offset) % period == 1,
                                 burst_101=(second.offset - first.offset) % period == 2,
                                 highest_seen_offset=second.offset)

    @classmethod
    def _update(cls, period: int, previous: 'GilbertCounts', last_three: deque) -> 'GilbertCounts':
        if len(last_three) != 3:
            raise Exception(f'Did not except `last_three` to have {len(last_three)} elements')
        first, second, third = last_three
        burst_11 = (third.offset - second.offset) % period == 1
        burst_101 = (third.offset - second.offset) % period == 2
        burst_111 = burst_11 and (second.offset - first.offset) % period == 1
        newly_seen_packets = (third.offset - previous.highest_seen_offset) % period
        return GilbertCounts(packet=previous.packet + newly_seen_packets,
                             loss=previous.loss + 1,
                             burst_11=previous.burst_11 + burst_11,
                             burst_101=previous.burst_101 + burst_101,
                             burst_111=previous.burst_111 + burst_111,
                             highest_seen_offset=third.offset)

    def to_params(self):
        try:
            p_1, p_11, p_101, p_111 = [count / self.packet for count
                                       in (self.loss, self.burst_11, self.burst_101,
                                           self.burst_111)]
            a, b = p_1, p_11
            c = p_111 / (p_101 + p_111)
            r = -1 * ((a * c - b * b) / (2 * a * c - b * (a + c)) - 1)
            h = 1 - (b / (1 - r))
            return {
                'p': a * r / (1 - h - a),
                'r': r,
                '1-h': 1 - h,
                '1-k': 0,
                'a': a,
                'b': b,
                'c': c
            }
        except ZeroDivisionError:
            return {}
