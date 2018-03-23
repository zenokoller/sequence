from itertools import tee
from operator import itemgetter
from typing import Iterable

from synchronizer.max_flow.alignment import Alignment
from synchronizer.max_flow.find_events import find_events

LOSS_COST = 1
REORDER_COST = 2
DUPE_COST = 5


def costs(alignments: Iterable[Alignment]) -> Iterable[int]:
    return (cost(a) for a in alignments)


def cost(alignment: Alignment) -> int:
    losses, reorders, dupes = find_events(alignment)
    return len(losses) * LOSS_COST + len(reorders) * REORDER_COST + len(dupes) * DUPE_COST


def choose_best(alignments: Iterable[Alignment]) -> Alignment:
    alignments, copy = tee(alignments)
    return sorted(zip(alignments, costs(copy)), key=itemgetter(1))[0][0]
