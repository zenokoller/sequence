from typing import Deque

from experiments.arrival.generator import Sequence
from simulator.utils import memory_one_coin_toss


class Waiting:
    __slots__ = ('item', 'remaining')

    def __init__(self, item: int, remaining: int):
        self.item = item
        self.remaining = remaining


def fixed_delay(sequence: Sequence,
                delay: int = 1,
                prob: int = 0,
                corr: int = 0,
                seed: int = None) -> Sequence:
    """Delays `prob` of packets by `delay`, correlated with the last delay by `corr`."""
    it = iter(sequence)
    toss = memory_one_coin_toss(prob=prob, corr=corr, seed=seed)
    queue: Deque[Waiting] = Deque()
    while True:
        if queue and queue[0].remaining == 0:
            yield queue.popleft().item
        for waiting in queue:
            waiting.remaining -= 1
        try:
            item = next(it)
            if next(toss):
                queue.append(Waiting(item=item, remaining=delay))
            else:
                yield item
        except StopIteration:
            return
