import socket
from functools import partial
from typing import Tuple, Callable

from sequence.sequence import DefaultSequence
from utils.call_repeatedly import call_repeatedly


def send_sequence(sock: socket.socket,
                  dest: Tuple[str, int],
                  sequence_cls: type = None,
                  seed=None,
                  sending_rate: int = None,
                  offset: int = None) -> Callable:
    """Sends symbols from a sequence on `socket` at `sending_rate` to `dest`. The sequence is
     derived as `sequence_fn(seed).`"""
    sequence = sequence_cls(seed, offset=offset)

    def send_symbol():
        sock.sendto(bytes([next(sequence)]), dest)

    stop = call_repeatedly(1 / sending_rate, send_symbol)

    return stop


send_default_sequence = partial(send_sequence, sequence_cls=DefaultSequence)
