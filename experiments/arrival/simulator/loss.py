from typing import Iterable

from simulator.random_process.ar1 import ar1
from simulator.random_process.random_process import RandomProcess
from simulator.random_process.state_machine import gilbert_elliot


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


def ge_loss(sequence: Iterable,
            move_to_bad=0.0,
            move_to_good=None,
            drop_in_bad=1.0,
            drop_in_good=0.0,
            seed: int = None) -> Iterable:
    return loss(gilbert_elliot(move_to_good=move_to_good,
                               move_to_bad=move_to_bad,
                               drop_in_bad=drop_in_bad,
                               drop_in_good=drop_in_good,
                               seed=seed), sequence)
