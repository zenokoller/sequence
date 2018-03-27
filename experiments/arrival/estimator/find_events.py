from itertools import accumulate
from typing import List, Dict

from estimator.events import Events
from synchronizer.alignment import Alignment


def find_events(alignment: Alignment) -> Events:
    losses = find_losses(alignment)
    delays = find_delays(alignment)
    dupes = find_dupe_candidates(alignment)
    return Events(losses=losses, delays=delays, dupes=dupes)


def find_losses(alignment: Alignment) -> List[int]:
    """Returns a list of reference indices that were lost."""
    offset, indices = alignment
    return sorted(set(range(offset, offset + len(indices))) - set(indices))


def find_delays(alignment: Alignment) -> Dict[int, int]:
    """Maps reference indeces of delayed packets to delay in number of packets."""
    offset, indices = alignment
    cum_dupes = accumulate([1 if a is None else 0 for _, a in enumerate(indices)])
    return {r_i: s_i + offset - r_i for s_i, (r_i, dupes) in enumerate(zip(indices, cum_dupes))
            if r_i is not None and r_i < s_i + offset - dupes}


def find_dupe_candidates(alignment: Alignment) -> List[int]:
    """Returns a list of signal indices of packets that were possibly duplicated."""
    _, indices = alignment
    return [s_i for s_i, r_i in enumerate(indices) if r_i is None]
