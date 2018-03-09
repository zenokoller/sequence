from typing import Deque, Iterable

from simulator.random_process.ar1 import ar1
from simulator.random_process.random_process import RandomProcess


class Waiting:
    __slots__ = ('item', 'remaining')

    def __init__(self, item: int, remaining: int):
        self.item = item
        self.remaining = remaining


def fixed_delay(process: RandomProcess, sequence: Iterable, delay: int = 1) -> Iterable:
    """Delays items from the `sequence` by `delay` items when the value drawn from `process` is
    true."""
    it = iter(sequence)
    queue: Deque[Waiting] = Deque()
    while True:
        if queue and queue[0].remaining == 0:
            yield queue.popleft().item
        for waiting in queue:
            waiting.remaining -= 1
        try:
            item = next(it)
            if next(process):
                queue.append(Waiting(item=item, remaining=delay))
            else:
                yield item
        except StopIteration:
            return


def ar1_fixed_delay(sequence: Iterable,
                    delay: int = 1,
                    prob: float = 0.0,
                    corr: float = 0.0,
                    seed: int = None) -> Iterable:
    return fixed_delay(ar1(prob=prob, corr=corr, seed=seed), sequence, delay=delay)
