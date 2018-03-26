from functools import partial
from typing import Deque, Callable, Iterable

from simulator.ground_truth.packet import Packet
from simulator.random_process.ar1 import ar1
from simulator.random_process.random_process import RandomProcess


class Waiting:
    __slots__ = ('packet', 'remaining')

    def __init__(self, packet: Packet, delay: int):
        self.packet = packet.set_delay(delay)
        self.remaining = delay


def _delay(process: RandomProcess,
           packets: Iterable[Packet],
           delay: Callable[[], int] = None) -> Iterable[Packet]:
    """Delays `packets` by `delay` when the value drawn from `process` is true and the packet is
    not lost."""
    it = iter(packets)
    queue: Deque[Waiting] = Deque()
    while True:
        if queue and queue[0].remaining == 0:
            yield queue.popleft().item
        for waiting in queue:
            waiting.remaining -= 1
        try:
            packet = next(it)
            if next(process) and not packet.is_lost:
                queue.append(Waiting(packet=packet, delay=delay()))
            else:
                yield packet
        except StopIteration:
            return


fixed_delay = partial(_delay, delay=lambda: 1)


def ar1_fixed_delay(sequence: Iterable,
                    delay: int = 1,
                    prob: float = 0.0,
                    corr: float = 0.0,
                    seed: int = None) -> Iterable:
    return fixed_delay(ar1(prob=prob, corr=corr, seed=seed), sequence, delay=delay)