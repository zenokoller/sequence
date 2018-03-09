from typing import List, Iterable

from simulator.simulator import Policy, simulator


def generate_permutation(policies: List[Policy], length: int) -> Iterable[int]:
    return simulator(range(length), policies)


def apply_permutation(original: list, permutation: Iterable[int]) -> list:
    """Applies the permutation to a list of values. Use when we want to retain a copy of the
    original values."""
    permuted = [0] * len(permutation)
    for new_index, old_index in enumerate(permutation):
        permuted[new_index] = original[old_index]
    return permuted
