from typing import Callable

from detect_events.detect_losses import detect_losses
from detect_events.detect_losses_and_reorderings import get_detect_losses_and_reorderings

DEFAULT_DETECT_EVENTS = detect_losses


def get_detect_events_fn(name: str, max_reorder_dist: int) -> Callable:
    if name == 'loss_and_reordering':
        return get_detect_losses_and_reorderings(max_reorder_dist)
    else:
        return DEFAULT_DETECT_EVENTS
