from enum import Enum
from typing import Callable, Iterable

from process_flows.synchronizer import Synchronizer
from sequence.generate import default_gen_sequence
from utils.drop import drop

State = Enum('State', 'sync no_sync')


class FlowProcessor:
    def __init__(self, seed: str, gen_sequence: Callable[[int], Iterable[int]] = None):
        self.seed = seed
        self.gen_sequence = gen_sequence

        self.state = State.sync
        self.pos = -1
        self.seq_iter = iter(self.gen_sequence(self.seed))
        self.syn = None

    def send(self, symbol: int):
        if self.state == State.no_sync:
            self.syn.send(symbol)
        elif symbol == next(self.seq_iter):
            self.pos += 1
        else:
            self.state = State.no_sync
            self.start_synchronizer(symbol)

    def start_synchronizer(self, symbol: int):
        def handle_synch_acquired(pos: int, mapping: dict):
            self.pos = pos
            self.seq_iter = iter(drop(self.gen_sequence(self.seed), self.pos))
            self.state = State.sync
            self.syn = None
            # TODO: derive_events(mapping)

        self.syn = Synchronizer(self.seed, last_pos=self.pos, first_symbol=symbol,
                                done=handle_synch_acquired)
        self.syn.send(symbol)

    @classmethod
    def default(cls, seed: int) -> 'FlowProcessor':
        return cls(seed, gen_sequence=default_gen_sequence)
