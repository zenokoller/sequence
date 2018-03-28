from random import Random
from typing import List, NamedTuple, Iterable, Callable, Tuple

from simulator.ground_truth.ground_truth import GroundTruth
from simulator.ground_truth.simulator import simulator
from simulator.policy import Policy
from utils import consume


class TestSignal(NamedTuple):
    signal: List[int]
    reference: List[int]
    ground_truth: GroundTruth

    @classmethod
    def generate(cls,
                 generator: Iterable[int] = None,
                 policies: List[Policy] = None,
                 sample_signal_lengths: Callable[[], Tuple[int, int]] = None,
                 must_contain_events: bool = False) -> 'TestSignal':
        signal_length, reference_length = sample_signal_lengths()

        reference = consume(generator, reference_length)
        offset = cls._sample_offset(signal_length, reference_length)

        sent_signal = reference[offset:offset + signal_length]
        signal, ground_truth = simulator(sent_signal, policies, offset=offset)

        while must_contain_events and ground_truth.number_of_events == 0:
            signal, ground_truth = simulator(sent_signal, policies, offset=offset)

        return TestSignal(signal=signal, reference=reference, ground_truth=ground_truth)

    @staticmethod
    def _sample_offset(sent_packets: int, reference_length: int) -> int:
        """Samples an offset of the signal uniformly at random."""
        return Random().randint(0, reference_length - sent_packets)
