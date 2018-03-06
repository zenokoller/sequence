from experiments.arrival.generator import Sequence
from simulator.utils import memory_one_coin_toss


def loss(sequence: Sequence,
         prob: int = 0,
         corr: int = 0,
         seed: int = None) -> Sequence:
    """Drops `sequence` items with probability `prob`, correlated with the last loss by `corr`."""
    it = iter(sequence)
    toss = memory_one_coin_toss(prob=prob, corr=corr, seed=seed)
    while True:
        try:
            if next(toss):
                next(it)
            else:
                yield next(it)
        except StopIteration:
            return
