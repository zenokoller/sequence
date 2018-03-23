from collections import Counter
from typing import List, Optional

from utils.sample_test_signal import TestSignal

"""For an alignment a, if a[i] is None then the i-th signal symbol is unaccounted for.
Otherwise, a[i] is the index of the reference position"""
Alignment = List[Optional[int]]


def expected_alignment(test_signal: TestSignal) -> Alignment:
    """Computes the expected alignment of a test signal."""
    _, _, permutation = test_signal
    counter = Counter(permutation)
    first_index = {key: permutation.index(key) for key in counter.keys()}
    return [p if i == first_index[p] or counter[p] == 1 else None for i, p in enumerate(
        permutation)]
