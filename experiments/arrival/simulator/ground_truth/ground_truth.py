from typing import NamedTuple, List, Dict, Iterable, Tuple

from simulator.ground_truth.packet import Packet


class GroundTruth(NamedTuple):
    losses: List[int]  # as reference indices
    delays: Dict[int, int]  # as reference index to delay in packets
    dupes: List[int]  # as signal indices

    @classmethod
    def from_packets(cls, packets: List[Packet], offset: int = 0) -> 'GroundTruth':
        return GroundTruth(losses=cls._get_loss_indices(packets, offset),
                           delays=cls._get_delays(packets, offset),
                           dupes=cls._get_duplicate_indices(packets))

    @staticmethod
    def _get_loss_indices(packets: List[Packet], offset: int) -> List[int]:
        return [packet.seq_nr + offset for packet in packets if packet.is_lost]

    @staticmethod
    def _get_delays(packets: List[Packet], offset: int) -> Dict[int, int]:
        return {packet.seq_nr + offset: packet.delay for packet in packets
                if packet.delay > 0 and not packet.is_duplicate}

    @staticmethod
    def _get_duplicate_indices(packets: List[Packet]) -> List[int]:
        return [i for i, packet in enumerate(packets) if packet.is_duplicate]
