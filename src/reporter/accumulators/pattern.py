from collections import deque
from functools import partial
from itertools import tee
from typing import Iterable

import numpy as np

from detector.events import Loss
from reporter.accumulators.rate import loss_rate
from reporter.accumulators.filter_last_n import filter_last_n_packets
from utils.coroutine import coroutine

DEFAULT_LAST_N_PACKETS = 1000
DEFAULT_BUFFER_SIZE = 10 ** 4
DEFAULT_MEDIAN_THRESHOLD = 2


@coroutine
def pattern_accumulator(period: int,
                        last_n_packets: int = DEFAULT_LAST_N_PACKETS,
                        median_threshold: int = DEFAULT_MEDIAN_THRESHOLD) -> dict:
    losses = deque(maxlen=last_n_packets)
    filter_relevant = partial(filter_last_n_packets, period, last_n_packets)

    def collect_values() -> dict:
        relevant_0, relevant_1 = tee(filter_relevant(losses))
        return {
            **{'loss_rate': loss_rate(period, relevant_0)},
            **detect_pattern(period, median_threshold, relevant_1)
        }

    while True:
        values = collect_values()
        event = yield values
        if isinstance(event, Loss):
            losses.append(event)


def detect_pattern(period: int, median_threshold: int, losses: Iterable[Loss]) -> dict:
    """Detects whether a loss pattern is random or correlated, based on whether the mode is 1 and
    a threshold on the median value."""
    bursts = np.fromiter(losses_to_bursts(period, losses), dtype=int)
    values, counts = np.unique(bursts, return_counts=True)

    if len(counts) == 0:
        return {}

    m = counts.argmax()
    mode = values[m]
    median = np.median(values)
    pattern = 'random' if mode == 1 and median < median_threshold else 'bursty'
    return {
        'pattern': pattern,
        'mode': int(mode),
        'median': int(median)
    }


def losses_to_bursts(period: int, losses: Iterable[Loss]) -> Iterable[int]:
    losses = iter(losses)

    burst = 1
    loss = next(losses)
    last_offset = loss.offset

    for loss in losses:
        if (loss.offset - last_offset) % period > 1:
            yield burst
            burst = 1
        else:
            burst += 1
        last_offset = loss.offset
    yield burst
