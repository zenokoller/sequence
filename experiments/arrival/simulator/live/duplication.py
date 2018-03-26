from typing import Iterable

from simulator.random_process.ar1 import ar1
from simulator.random_process.random_process import RandomProcess


def duplication(process: RandomProcess, sequence: Iterable) -> Iterable:
    """Duplicates items from the `sequence` when the value drawn from `process` is true."""
    it = iter(sequence)
    while True:
        try:
            previous = next(it)
        except StopIteration:
            return
        yield previous
        if next(process):
            yield previous


def ar1_duplication(sequence: Iterable, prob=0.0, corr=0.0, seed: int = None) -> Iterable:
    return duplication(ar1(prob, corr, seed=seed), sequence)
