from collections import Iterable
from typing import List, Tuple

from simulator.simulator import Policy
from synchronizer.range_matcher.base_synchronizer import Synchronizer
from synchronizer.range_matcher.estimator import Estimator
from utils.sample_test_signal import sample_test_signal


def run_synch_estim_pair(synchronizer: Synchronizer,
                         estimator: Estimator,
                         generator: Iterable = None,
                         policies: List[Policy] = None,
                         reference_length: int = None) -> Tuple[List[int], List[int]]:
    def sample_signal_lengths():
        return reference_length, reference_length

    signal, reference, permutation = sample_test_signal(generator=generator,
                                                        policies=policies,
                                                        sample_signal_lengths=sample_signal_lengths)
    expected = sorted(set(range(reference_length)) - set(permutation))
    actual = estimator(reference, signal, synchronizer(reference, signal))
    return expected, actual


def rel_mean_dist_err(expected: List[int], actual: List[int]) -> float:
    """Returns the relative error in the mean distance between the indices of `expected` and
    `actual`."""
    if len(expected) <= 1:
        return 0
    expected_mean_dist, actual_mean_dist = [mean_distance(list_) for list_ in (expected, actual)]
    return abs(actual_mean_dist - expected_mean_dist) / expected_mean_dist


def mean_distance(indices: List[int]):
    if len(indices) <= 1:
        return 0
    else:
        return sum(i2 - i1 for i1, i2 in zip(indices[:-1], indices[1:])) / (len(indices) - 1)
