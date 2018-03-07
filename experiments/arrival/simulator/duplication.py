from experiments.arrival.generator import Sequence
from simulator.random_process import RandomProcess, ar1


def duplication(process: RandomProcess, sequence: Sequence) -> Sequence:
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


def ar1_duplication(sequence: Sequence, prob=0.0, corr=0.0, seed: int = None) -> Sequence:
    return duplication(ar1(prob, corr, seed=seed), sequence)
