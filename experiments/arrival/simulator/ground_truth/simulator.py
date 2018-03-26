from typing import Iterable, List, Tuple

from simulator.ground_truth.ground_truth import GroundTruth
from simulator.ground_truth.packet import reference_to_packets, packets_to_signal
from simulator.policy import Policy
from utils import consume_all


def simulator(sequence: Iterable,
              policies: List[Policy],
              offset: int = 0) -> Tuple[List[int], GroundTruth]:
    """Applies the given policies to the sequence, yields the resulting sequence along with
    ground truth (the losses, duplicates and delays that actually happened).
    If `offset` is given, the loss and delay indices will be adjusted."""
    packet_gen = reference_to_packets(sequence)
    for policy in policies:
        packet_gen = (p for p in policy(packet_gen))
    packets = consume_all(packet_gen)
    return packets_to_signal(packets), GroundTruth.from_packets(packets, offset=offset)
