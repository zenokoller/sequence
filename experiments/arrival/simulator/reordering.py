from typing import Deque

from experiments.arrival.generator import Sequence
from simulator.random_process import RandomProcess, ar1


class Waiting:
    __slots__ = ('item', 'remaining')

    def __init__(self, item: int, remaining: int):
        self.item = item
        self.remaining = remaining


def fixed_delay(process: RandomProcess, sequence: Sequence, delay: int = 1) -> Sequence:
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


def ar1_fixed_delay(sequence: Sequence,
                    delay: int = 1,
                    prob: float = 0.0,
                    corr: float = 0.0,
                    seed: int = None) -> Sequence:
    return fixed_delay(ar1(prob=prob, corr=corr, seed=seed), sequence, delay=delay)
