from functools import partial
from random import Random
from typing import List, NamedTuple, Iterable

from generator.sequence import generate_random_sequence
from simulator.loss import ge_loss
from simulator.permutation import generate_permutation, apply_permutation
from simulator.simulator import Policy
from utils import consume, consume_all

TestSignal = NamedTuple('TestSignals', [
    ('signal', List[int]),
    ('reference', List[int]),
    ('permutation', List[int])  # used to obtain signal from reference
])


def sample_test_signal(generator: Iterable[int],
                       policies: List[Policy],
                       sent_packets: int = None,
                       reference_length: int = None) -> TestSignal:
    reference = consume(generator, reference_length)
    offset = sample_offset(sent_packets, reference_length)

    sent_signal = reference[offset:offset + sent_packets]
    permutation = consume_all(i + offset for i in generate_permutation(policies, len(sent_signal)))
    sig = apply_permutation(reference, permutation)

    return TestSignal(signal=sig, reference=reference, permutation=permutation)


def sample_offset(sent_packets: int, reference_length: int) -> int:
    """Samples an offset of the signal uniformly at random."""
    return Random().randint(0, reference_length - sent_packets)
