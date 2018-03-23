from itertools import accumulate
from typing import List, Dict, NamedTuple

from synchronizer.max_flow.alignment import Alignment

Events = NamedTuple('Events', [
    ('losses', List[int]),
    ('reorders', Dict[int, int]),
    ('dupes', List[int])
])


def find_events(alignment: Alignment) -> Events:
    losses = find_losses(alignment)
    reorders = find_reorders(alignment)
    dupes = find_dupe_candidates(alignment)
    return Events(losses=losses, reorders=reorders, dupes=dupes)


def find_losses(alignment: Alignment) -> List[int]:
    """Returns a list of reference indices that were lost."""
    offset = get_offset(alignment)
    return sorted(set(range(offset, offset + len(alignment))) - set(alignment))


def find_reorders(alignment: Alignment) -> Dict[int, int]:
    """Maps reference indeces of reordered packets to delay in number of packets."""
    offset = get_offset(alignment)
    cum_dupes = accumulate([1 if a is None else 0 for _, a in enumerate(alignment)])
    return {r_i: s_i + offset - r_i for s_i, (r_i, dupes) in enumerate(zip(alignment, cum_dupes))
            if r_i is not None and r_i < s_i + offset - dupes}


def find_dupe_candidates(alignment: Alignment) -> List[int]:
    """Returns a list of signal indices of packets that were possibly duplicated."""
    return [s_i for s_i, r_i in enumerate(alignment) if r_i is None]


def get_offset(alignment: Alignment) -> int:
    return next(a for a in alignment if a is not None)
