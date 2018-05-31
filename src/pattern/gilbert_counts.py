from collections.__init__ import deque
from functools import partial
from typing import NamedTuple, Iterable

from detector.events import Event, Loss


class GilbertCounts(NamedTuple):
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
    packet: int = 0
    loss: int = 0
    burst_11: int = 0
    burst_101: int = 0
    burst_111: int = 0
    highest_seen_offset: int = 0

    @classmethod
    def from_events(cls, period: int, events: Iterable[Event]) -> 'GilbertCounts':
        loss_offsets = (event.offset for event in events if isinstance(event, Loss))
        return GilbertCounts.from_loss_offsets(period, loss_offsets)

    @classmethod
    def from_loss_offsets(cls, period: int, offsets: Iterable[int]) -> 'GilbertCounts':
        offsets = iter(offsets)
        update = partial(GilbertCounts._update, period)
        first_two = (next(offsets, None), next(offsets, None))
        counts = GilbertCounts._from_first_two_loss_offsets(period, *first_two)
        last_three = deque(maxlen=3)
        last_three.extend(first_two)
        for offset in offsets:
            last_three.append(offset)
            counts = update(counts, last_three)
        return counts

    @classmethod
    def _from_first_two_loss_offsets(cls, period: int, first: int, second: int):
        if first is None:
            return GilbertCounts()
        elif second is None:
            return GilbertCounts(loss=1, highest_seen_offset=first)
        else:
            return GilbertCounts(packet=(second - first) % period,
                                 loss=2,
                                 burst_11=(second - first) % period == 1,
                                 burst_101=(second - first) % period == 2,
                                 highest_seen_offset=second)

    @classmethod
    def _update(cls, period: int, previous: 'GilbertCounts', last_three: deque) -> 'GilbertCounts':
        if len(last_three) != 3:
            raise Exception(f'Did not except `last_three` to have {len(last_three)} elements')
        first, second, third = last_three
        burst_11 = (third - second) % period == 1
        burst_101 = (third - second) % period == 2
        burst_111 = burst_11 and (second - first) % period == 1
        newly_seen_packets = (third - previous.highest_seen_offset) % period
        return GilbertCounts(packet=previous.packet + newly_seen_packets,
                             loss=previous.loss + 1,
                             burst_11=previous.burst_11 + burst_11,
                             burst_101=previous.burst_101 + burst_101,
                             burst_111=previous.burst_111 + burst_111,
                             highest_seen_offset=third)

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
