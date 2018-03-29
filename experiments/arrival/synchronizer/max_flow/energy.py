from functools import partial

DEFAULT_DELAY_PENALTY = 2
DEFAULT_DISCRETIZE_FACTOR = 50


def edge_energy(shift: int,
                common_subsequence_length: int,
                delay_penalty: int = None,
                discretize_factor: int = None) -> int:
    p = delay_penalty if shift < 0 else 1
    return p * int(discretize_factor * (1 + abs(shift)) / common_subsequence_length)


default_edge_energy = partial(edge_energy,
                              delay_penalty=DEFAULT_DELAY_PENALTY,
                              discretize_factor=DEFAULT_DISCRETIZE_FACTOR)
