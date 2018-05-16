import socket
from typing import Callable

from utils.call_repeatedly import call_repeatedly
from utils.integer_codec import encode_symbol_with_offset
from utils.types import Address


def send_sequence(sock: socket.socket,
                  dest: Address,
                  sequence_cls: type = None,
                  seed: int = None,
                  sending_rate: int = None,
                  offset: int = None) -> Callable:
    """Sends symbols from a sequence on `socket` at `sending_rate` to `dest`. The sequence is
     derived as `sequence_fn(seed).`"""
    sequence = sequence_cls(seed, offset=offset)

    def send_symbol():
        payload = encode_symbol_with_offset(next(sequence))
        sock.sendto(payload, dest)

    stop = call_repeatedly(1 / sending_rate, send_symbol)

    return stop
