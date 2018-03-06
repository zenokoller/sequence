from random import Random
from typing import Generator


def memory_one_coin_toss(prob: int = 0,
                         corr: int = 0,
                         seed: int = None) -> Generator[bool, None, None]:
    """Simulates a series of coin tosses with success probability `prob` such that the current
    toss depends on the previous toss with correlation `corr`."""
    r = Random(seed)
    prev = r.random()
    yield prev < prob
    while True:
        prev = r.random() * (1 - corr) + corr * prev
        yield prev < prob
