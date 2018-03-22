from itertools import accumulate
from typing import List, Tuple, Dict

from synchronizer.max_flow.alignment import Alignment


def find_events(sig: List[int], alignment: Alignment) -> Tuple[list, dict, list]:
    losses = find_losses(sig, alignment)
    reorders = find_reorders(alignment)
    dupes = find_dupe_candidates(alignment)
    return losses, reorders, dupes


def find_losses(sig: List[int], alignment: Alignment) -> List[int]:
    """Returns a list of reference indices that were lost."""
    offset = min(r_i for r_i in alignment if r_i is not None)
    return sorted(set(range(offset, offset + len(sig))) - set(alignment))


def find_reorders(alignment: Alignment) -> Dict[int, int]:
    """Maps reference indeces of reordered packets to delay in number of packets."""
    offset = min(r_i for r_i in alignment if r_i is not None)
    cum_dupes = accumulate([1 if a is None else 0 for _, a in enumerate(alignment)])
    return {r_i: s_i + offset - r_i for s_i, (r_i, dupes) in enumerate(zip(alignment, cum_dupes))
            if r_i is not None and r_i < s_i + offset - dupes}


def find_dupe_candidates(alignment: Alignment) -> List[int]:
    """Returns a list of signal indices of packets that were possibly duplicated."""
    return [s_i for s_i, r_i in enumerate(alignment) if r_i is None]


def print_events(sig: List[int], ref: List[int], alignment: Alignment, events: Tuple[list, dict,
                                                                                     list]):
    offset = min(r_i for r_i in alignment if r_i is not None)
    left_col_width = 10

    losses, reorders, dupes = events

    dupes_str = " ".join("d" if i in dupes else " " for i in range(len(ref)))
    print(f'{"dupes".rjust(left_col_width)} | {dupes_str}')

    sig_str = "  " * offset + " ".join(str(s) for s in sig)
    print(f'{"SIGNAL".rjust(left_col_width)} | {sig_str}')
    ref_str = " ".join(str(r) for r in ref)
    print(f'{"REFERENCE".rjust(left_col_width)} | {ref_str}')

    loss_str = " ".join("x" if i in losses else " " for i in range(len(ref)))
    print(f'{"losses".rjust(left_col_width)} | {loss_str}')

    reorder_str = " ".join(str(reorders.get(i, " ")) for i in range(len(ref)))
    print(f'{"reorders".rjust(left_col_width)} | {reorder_str}')
