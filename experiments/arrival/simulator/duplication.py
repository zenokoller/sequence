from experiments.arrival.generator import Sequence
from simulator.utils import memory_one_coin_toss


def duplication(sequence: Sequence,
                prob: int = 0,
                corr: int = 0,
                seed: int = None) -> Sequence:
    """Duplicates `sequence` items with probability `prob`,
    correlated with the last duplicate by `corr`."""
    it = iter(sequence)
    toss = memory_one_coin_toss(prob=prob, corr=corr, seed=seed)
    while True:
        try:
            previous = next(it)
        except StopIteration:
            return
        yield previous
        if next(toss):
            yield previous
