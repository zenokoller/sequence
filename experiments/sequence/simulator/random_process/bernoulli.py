from random import Random

from .random_process import RandomProcess


def bernoulli(prob=0.0, seed: int = None) -> RandomProcess:
    """Two-state model with uncorrelated loss events."""
    r = Random(seed)
    while True:
        yield True if r.random() < prob else False
