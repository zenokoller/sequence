from random import Random

from simulator.random_process.random_process import RandomProcess


def ar1(prob=0.0, corr=0.0, seed: int = None) -> RandomProcess:
    """See: https://en.wikipedia.org/wiki/Autoregressive_model"""
    r = Random(seed)
    prev = r.random()
    yield prev < prob
    while True:
        prev = r.random() * (1 - corr) + corr * prev
        yield prev < prob
