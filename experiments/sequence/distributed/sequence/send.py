import socket
from functools import partial
from typing import Tuple, Callable, Sequence

from sequence.sequence import get_default_sequence
from utils.call_repeatedly import call_repeatedly


def send_sequence(sock: socket.socket,
                  dest: Tuple[str, int],
                  get_sequence: Callable[[str], Sequence] = None,
                  seed: str = None,
                  sending_rate: int = None) -> Callable:
    """Sends symbols from a sequence on `socket` at `sending_rate` to `dest`. The sequence is
     derived as `sequence_fn(seed).`"""
    sequence = get_sequence(seed)

    def send_symbol():
        sock.sendto(bytes([next(sequence)]), dest)

    stop = call_repeatedly(1 / sending_rate, send_symbol)

    return stop


send_default_sequence = partial(send_sequence, get_sequence=get_default_sequence)
