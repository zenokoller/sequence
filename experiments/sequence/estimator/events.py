from typing import NamedTuple, List, Dict


class Events(NamedTuple):
    losses: List[int]  # as reference indices
    delays: Dict[int, int]  # as reference index to delay in packets
    dupes: List[int]  # as signal indices

    @property
    def number_of_events(self):
        return len(self.losses) + len(self.delays) + len(self.dupes)
