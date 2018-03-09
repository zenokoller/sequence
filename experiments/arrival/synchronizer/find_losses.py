from difflib import SequenceMatcher
from typing import List, Tuple, Dict, Iterable

Range = Tuple[int, int]


def find_losses(orig: List[int], recv: List[int]) -> List[int]:
    """Finds the loss indices, where an element in the original array was lost.
    Returns an array of indices of the lost elements from orig. Assumes that there are _only_
    losses and no duplicates or reorderings."""
    losses = _get_loss_mask(orig, recv)
    return [i for i, loss in enumerate(losses) if loss]


def _get_loss_mask(orig: List[int], recv: List[int]) -> List[bool]:
    losses = [True] * len(orig)

    def update_losses(range_: Range):
        i, j = range_
        losses[i:j] = [False] * (j - i)

    def longest_subranges(orig_full: Range, recv_full: Range) -> Tuple[Range, Range]:
        of1, of2 = orig_full
        rf1, rf2 = recv_full
        seq1, seq2 = orig[of1:of2], recv[rf1:rf2]
        m = SequenceMatcher(None, seq1, seq2).find_longest_match(0, len(seq1), 0, len(seq2))
        return (of1 + m.a, of1 + m.a + m.size), (rf1 + m.b, rf1 + m.b + m.size)

    def align_subranges(orig_full: Range, recv_full: Range) -> Dict[Range, Range]:
        orig_sub, recv_sub = longest_subranges(orig_full, recv_full)
        update_losses(orig_sub)
        return remaining_ranges(orig_full, orig_sub, recv_full, recv_sub)

    ranges = {(0, len(orig)): (0, len(recv))}
    while len(ranges) > 0:
        ranges = merge_dicts(align_subranges(o, r) for o, r in ranges.items())
    return losses


def merge_dicts(dicts: Iterable[dict]) -> dict:
    return {k: v for d in dicts for k, v in d.items()}


def remaining_ranges(orig_full: Range,
                     orig_sub: Range,
                     recv_full: Range,
                     recv_sub: Range) -> Dict[Range, Range]:
    of1, of2 = orig_full
    os1, os2 = orig_sub
    rf1, rf2 = recv_full
    rs1, rs2 = recv_sub
    ranges = {}
    if of1 < os1 and rf1 < rs1:
        ranges[(of1, os1)] = (rf1, rs1)
    if os2 < of2 and rs2 < rf2:
        ranges[(os2, of2)] = (rs2, rf2)
    return ranges
