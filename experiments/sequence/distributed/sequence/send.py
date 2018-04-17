import socket
from functools import partial
from typing import Tuple, Callable, Iterable

from utils.call_repeatedly import call_repeatedly
from sequence.generate import generate_random_sequence


def send_sequence(sock: socket.socket,
                  dest: Tuple[str, int],
                  sequence_fn: Callable[[int], Iterable[int]] = None,
                  seed: int = None,
                  sending_rate: int = None) -> Callable:
    """Sends symbols from a sequence on `socket` at `sending_rate` to `dest`. The sequence is
     derived as `sequence_fn(seed).`"""
    sequence = sequence_fn(seed)
    it = iter(sequence)

    def send_symbol():
        sock.sendto(bytes([next(it)]), dest)

    stop = call_repeatedly(1 / sending_rate, send_symbol)

    return stop


random_sequence = partial(generate_random_sequence, 2)
send_random_sequence = partial(send_sequence, sequence_fn=random_sequence)
