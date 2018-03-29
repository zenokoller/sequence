from itertools import accumulate
from typing import List, Dict

from estimator.events import Events
from simulator.ground_truth.packet import Packet


class GroundTruth(Events):
    @classmethod
    def from_packets(cls, packets: List[Packet], offset: int = 0) -> 'GroundTruth':
        loss_indices = cls._get_loss_indices(packets, offset)
        return cls(losses=loss_indices,
                   delays=cls._get_delays(packets, offset),
                   dupes=cls._get_duplicate_indices(packets, loss_indices))

    @staticmethod
    def _get_loss_indices(packets: List[Packet], offset: int) -> List[int]:
        return [packet.seq_nr + offset for packet in packets if packet.is_lost]

    @staticmethod
    def _get_delays(packets: List[Packet], offset: int) -> Dict[int, int]:
        return {packet.seq_nr + offset: packet.delay for packet in packets
                if packet.delay > 0 and not packet.is_duplicate}

    @staticmethod
    def _get_duplicate_indices(packets: List[Packet], loss_indices: List[int]) -> List[int]:
        loss_cumsum = accumulate([1 if i in loss_indices else 0 for i in range(len(packets))])
        return [i - num_lost for i, (packet, num_lost)
                in enumerate(zip(packets, loss_cumsum)) if packet.is_duplicate]
