from typing import Iterable

from simulator.random_process.ar1 import ar1
from simulator.random_process.random_process import RandomProcess


def loss(process: RandomProcess, sequence: Iterable) -> Iterable:
    """Drops items from the `sequence` when the value drawn from `process` is true."""
    it = iter(sequence)
    while True:
        try:
            if next(process):
                next(it)
            else:
                yield next(it)
        except StopIteration:
            return


def ar1_loss(sequence: Iterable, prob=0.0, corr=0.0, seed: int = None) -> Iterable:
    return loss(ar1(prob=prob, corr=corr, seed=seed), sequence)
