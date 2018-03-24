from collections import Counter
from random import Random
from typing import List, NamedTuple, Iterable, Callable, Tuple

from simulator.permutation import generate_permutation, apply_permutation
from simulator.simulator import Policy
from synchronizer.max_flow.alignment import Alignment
from utils import consume, consume_all


class TestSignal(NamedTuple):
    signal: List[int]
    reference: List[int]
    permutation: List[int]  # used to obtain signal from reference

    @classmethod
    def sample(cls, generator: Iterable[int] = None,
               policies: List[Policy] = None,
               sample_signal_lengths: Callable[[], Tuple[int, int]] = None) -> 'TestSignal':
        signal_length, reference_length = sample_signal_lengths()

        reference = consume(generator, reference_length)
        offset = cls._sample_offset(signal_length, reference_length)

        sent_signal = reference[offset:offset + signal_length]
        permutation = consume_all(
            i + offset for i in generate_permutation(policies, len(sent_signal)))
        sig = apply_permutation(reference, permutation)

        return TestSignal(signal=sig, reference=reference, permutation=permutation)

    @staticmethod
    def _sample_offset(sent_packets: int, reference_length: int) -> int:
        """Samples an offset of the signal uniformly at random."""
        return Random().randint(0, reference_length - sent_packets)

    @property
    def expected_alignment(self) -> Alignment:
        """Computes the expected alignment of a test signal."""
        counter = Counter(self.permutation)
        first_index = {key: self.permutation.index(key) for key in counter.keys()}
        return [p if i == first_index[p] or counter[p] == 1 else None for i, p in enumerate(
            self.permutation)]
