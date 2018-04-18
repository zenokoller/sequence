import socket
from functools import partial
from typing import Iterable, Tuple, Callable

from process_flows.flow_processor import default_flow_processor


def demux_socket(sock: socket.socket,
                 flow_processor_from_seed: Callable = None,
                 seed_from_addr_port: Callable = None):
    """Receives symbols from a socket and starts a flow processor for each seen flow id."""
    flow_processors = {}

    for addr_port, symbol in receive_from_socket(sock):
        flow_proc = flow_processors.get(addr_port, None)

        if flow_proc is None:
            seed = seed_from_addr_port(*addr_port)
            flow_proc = flow_processor_from_seed(seed)
            next(flow_proc)
            flow_processors[addr_port] = flow_proc

        flow_proc.send(symbol)


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


default_demux_socket = partial(demux_socket, flow_processor_from_seed=default_flow_processor)
