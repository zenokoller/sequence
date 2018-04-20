from typing import Callable

from process_flows.buffer_bytes import buffer_bytes


class Synchronizer:
    def __init__(self,
                 seed: str,
                 last_pos: int,
                 first_symbol: int,
                 done=Callable[[int, dict], None]):
        self.seed = seed
        self.last_pos = last_pos
        self.done = done
        self.bytes = bytearray()
        self.buffer = buffer_bytes(self.bytes, first_symbol)

    def send(self, symbol):
        self.buffer.send(symbol)
