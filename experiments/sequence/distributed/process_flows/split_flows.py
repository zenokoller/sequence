import socket
from functools import partial
from typing import Iterable, Tuple, Callable, Coroutine

from process_flows.synchronize import default_synchronize


def split_flows_with_socket(sock: socket.socket,
                            synchronize: Callable = None,
                            seed_from_addr_port: Callable = None):
    split_flows(receive_from_socket(sock),
                synchronize=synchronize,
                seed_from_addr_port=seed_from_addr_port)


def split_flows_with_trace():
    raise NotImplementedError


def split_flows(input: Iterable[Tuple[str, int]],
                synchronize: Callable[[str], Coroutine] = None,
                seed_from_addr_port: Callable = None):
    """Receives symbols from a socket and starts a flow processor for each seen flow id."""
    synchronizers = {}

    for addr_port, symbol in input:
        sync = synchronizers.get(addr_port, None)

        if sync is None:
            seed = seed_from_addr_port(*addr_port)
            sync = synchronize(seed)
            synchronizers[addr_port] = sync

        sync.send(symbol)


def receive_from_socket(sock: socket.socket,
                        reflect: bool = False) -> Iterable[Tuple[Tuple[str, int], int]]:
    """Receive sequence on socket `sock` and optionally reflect it."""
    while True:
        data, address = sock.recvfrom(1024)
        if not data:
            break
        if reflect:
            sock.sendto(data, address)
        yield address, int.from_bytes(data, byteorder='little')


default_split_flows_with_socket = partial(split_flows_with_socket,
                                          synchronize=default_synchronize)
