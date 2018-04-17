import socket
from functools import partial
from typing import Iterable, Callable, Union

from client.call_repeatedly import call_repeatedly
from generator.sequence import generate_random_sequence


def send_sequence(src_port: int,
                  dst_ip: str,
                  dst_port: int,
                  sequence_fn: Callable[[int], Iterable[int]] = None,
                  seed: int = None,
                  sending_rate: int = None):
    """Sends symbols from a sequence to `dst_ip:dst_port` via UDP at `sending_rate`. The sequence is
     derived as `sequence_fn(seed).`"""
    sequence = sequence_fn(seed)
    it = iter(sequence)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', src_port))

    def send_symbol():
        sock.sendto(bytes([next(it)]), (dst_ip, dst_port))

    _ = call_repeatedly(1 / sending_rate, send_symbol)


random_sequence = partial(generate_random_sequence, 2)
send_random_sequence = partial(send_sequence, sequence_fn=random_sequence)
