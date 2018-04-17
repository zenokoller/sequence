from typing import Iterable

from simulator.ground_truth.packet import Packet
from simulator.random_process.ar1 import ar1
from simulator.random_process.random_process import RandomProcess
from simulator.random_process.state_machine import gilbert_elliot


def loss(process: RandomProcess, packets: Iterable[Packet]) -> Iterable[Packet]:
    """Marks packets as lost when the value drawn from `process` is true."""
    it = iter(packets)
    while True:
        try:
            packet = next(it)
        except StopIteration:
            return

        if next(process) and not packet.is_lost:
            yield packet.mark_lost()
        else:
            yield packet


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
