import logging
import socket
from functools import partial
from typing import Callable

from sequence.sequence import DefaultSequence
from utils.call_repeatedly import call_repeatedly
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
        offset = sequence.offset
        symbol = next(sequence)
        logging.debug(f'send_symbol: offset={offset}, symbol={symbol}')
        sock.sendto(bytes([symbol]), dest)

    stop = call_repeatedly(1 / sending_rate, send_symbol)

    return stop


send_default_sequence = partial(send_sequence, sequence_cls=DefaultSequence)
