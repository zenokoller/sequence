from typing import Iterable

from simulator.random_process.ar1 import ar1
from simulator.random_process.random_process import RandomProcess


def duplication(process: RandomProcess, packets: Iterable) -> Iterable:
    """Duplicates packets and marks them as a duplicate."""
    it = iter(packets)
    while True:
        try:
            previous = next(it)
        except StopIteration:
            return
        yield previous
        if next(process) and not previous.is_lost:
            yield previous.as_duplicate()


def ar1_duplication(sequence: Iterable, prob=0.0, corr=0.0, seed: int = None) -> Iterable:
    return duplication(ar1(prob, corr, seed=seed), sequence)
