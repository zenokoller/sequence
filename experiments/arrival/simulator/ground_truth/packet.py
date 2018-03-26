from typing import NamedTuple, Iterable, List


class Packet(NamedTuple):
    seq_nr: int
    symbol: int
    is_lost: bool = False
    delay: int = 0
    is_duplicate: bool = False

    def mark_lost(self) -> 'Packet':
        return self._replace(is_lost=True)

    def set_delay(self, delay: bool) -> 'Packet':
        return self._replace(delay=delay)

    def as_duplicate(self) -> 'Packet':
        return self._replace(is_duplicate=True)


def reference_to_packets(ref: Iterable[int]) -> Iterable[Packet]:
    return (Packet(seq_nr=i, symbol=symbol) for i, symbol in enumerate(ref))


def packets_to_signal(packets: List[Packet]) -> List[int]:
    return [packet.symbol for packet in packets if not packet.is_lost]
