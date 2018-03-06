from functools import reduce
from typing import List, Callable

from experiments.arrival.generator import Sequence

Policy = Callable[[Sequence], Sequence]


def simulator(sequence: Sequence, policies: List[Policy]) -> Sequence:
    """Applies the given `policies` to `input_` and returns the resulting sequence."""
    chain = reduce(lambda p, q: q(p), policies[1:], policies[0](sequence)) if len(policies) > 0 \
        else iter(sequence)
    while True:
        try:
            yield next(chain)
        except StopIteration:
            return
