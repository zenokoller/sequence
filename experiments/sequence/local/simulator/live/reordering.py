from random import Random
from typing import Deque, Iterable, Callable, Tuple

from simulator.random_process.ar1 import ar1
from simulator.random_process.random_process import RandomProcess


class Waiting:
    __slots__ = ('symbol', 'remaining')

    def __init__(self, symbol: int, remaining: int):
        self.symbol = symbol
        self.remaining = remaining


def _delay(process: RandomProcess, sequence: Iterable, delay: Callable[[], int] = None) -> Iterable:
    """Delays `sequence` symbols by `delay` symbols when the value drawn from `process` is true."""
    it = iter(sequence)
    queue: Deque[Waiting] = Deque()
    while True:
        if queue and queue[0].remaining == 0:
            yield queue.popleft().symbol
        for waiting in queue:
            waiting.remaining -= 1
        try:
            symbol = next(it)
            if next(process):
                queue.append(Waiting(symbol=symbol, remaining=delay()))
            else:
                yield symbol
        except StopIteration:
            return


def ar1_fixed_delay(sequence: Iterable,
                    delay: int = 1,
                    prob: float = 0.0,
                    corr: float = 0.0,
                    seed: int = None) -> Iterable:
    return _delay(ar1(prob=prob, corr=corr, seed=seed), sequence, delay=lambda: delay)


def ar1_uniform_delay(sequence: Iterable,
                      delay_bounds: Tuple[int, int] = (1, 5),
                      prob: float = 0.0,
                      corr: float = 0.0,
                      seed: int = None) -> Iterable:
    return _delay(ar1(prob=prob, corr=corr, seed=seed),
                  sequence,
                  delay=lambda: Random().randint(*delay_bounds))
