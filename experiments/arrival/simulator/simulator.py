from functools import reduce
from typing import List, Callable, Iterable

Policy = Callable[[Iterable], Iterable]
"""A function that takes an iterable, applies a policy (loss, reordering or duplication) and 
returns the result as an iterable."""


def simulator(sequence: Iterable, policies: List[Policy]) -> Iterable:
    """Applies the given `policies` to `input_` and returns the resulting sequence."""
    chain = reduce(lambda p, q: q(p), policies[1:], policies[0](sequence)) if len(policies) > 0 \
        else iter(sequence)
    while True:
        try:
            yield next(chain)
        except StopIteration:
            return
