from random import Random
from typing import List, NamedTuple, Iterable, Callable, Union, Tuple

from simulator.permutation import generate_permutation, apply_permutation
from simulator.simulator import Policy
from utils import consume, consume_all

TestSignal = NamedTuple('TestSignals', [
    ('signal', List[int]),
    ('reference', List[int]),
    ('permutation', List[int])  # used to obtain signal from reference
])


def sample_test_signal(generator: Iterable[int] = None,
                       policies: List[Policy] = None,
                       sample_signal_lengths: Callable[[], Tuple[int, int]] = None) -> TestSignal:
    signal_length, reference_length = sample_signal_lengths()

    reference = consume(generator, reference_length)
    offset = sample_offset(signal_length, reference_length)

    sent_signal = reference[offset:offset + signal_length]
    permutation = consume_all(i + offset for i in generate_permutation(policies, len(sent_signal)))
    sig = apply_permutation(reference, permutation)

    return TestSignal(signal=sig, reference=reference, permutation=permutation)


def sample_offset(sent_packets: int, reference_length: int) -> int:
    """Samples an offset of the signal uniformly at random."""
    return Random().randint(0, reference_length - sent_packets)
