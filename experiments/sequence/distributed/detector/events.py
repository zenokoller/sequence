from typing import NamedTuple, List, Dict


class Events(NamedTuple):
    losses: List[int]  # as sequence indices
    delays: Dict[int, int]  # as sequence index to delay in packets
    dupes: List[int]  # as sequence indices
    # TODO: Add timing information
