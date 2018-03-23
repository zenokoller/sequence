from functools import reduce
from typing import List, Iterable

from simulator.policy import Policy


def simulator(sequence: Iterable, policies: List[Policy]) -> Iterable:
    """Applies the given `policies` to `sequence` and yields the resulting sequence."""
    chain = reduce(lambda p, q: q(p), policies[1:], policies[0](sequence)) if len(policies) > 0 \
        else iter(sequence)
    while True:
        try:
            yield next(chain)
        except StopIteration:
            return
