from array import array
from typing import Tuple, List

from detector.event import Events, Loss

DetectInput = Tuple[int, array, array]


def detect_losses(offset: int, actual: array, expected: array, found_offset: int) -> List[
    Loss]:
    if len(actual) == 0:
        return [Loss(offset, len(expected), found_offset)]
    else:
        return []


Missing = List[array]


def detect_events(offset: int, actual: array, expected: array, missing) -> Tuple[Events, Missing]:
    """Signature subject to change, need to add timing information for expected symbols. Here,
    we probably have to find matching parts first instead of a recursive apporoach as in the
    loss-only solution."""
    raise NotImplementedError
