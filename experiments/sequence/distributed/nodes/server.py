from argparse import ArgumentParser
from asyncio import get_event_loop, Queue, ensure_future
from functools import partial
from typing import Dict

from sequence.seed import seed_from_addresses
from synchronizer.synchronizer import DefaultSynchronizer
from utils.ip import get_my_ip
from utils.types import Address

parser = ArgumentParser()
parser.add_argument('local_port', type=int)
parser.add_argument('-e', '--echo', action='store_true')
args = parser.parse_args()

local_ip, local_port = get_my_ip(), args.local_port

get_seed = partial(seed_from_addresses, recv_addr=(local_ip, local_port))

Synchronizer = DefaultSynchronizer


class SequenceServerProtocol:
    def __init__(self, echo=False):
        self.echo = echo
        self.transport = None
        self.queues: Dict[Address: Queue] = {}

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        queue = self.queues.get(addr, None)
        if queue is None:
            queue = self.new_synchronizer(addr)
            self.queues[addr] = queue

        queue.put_nowait(self.decode_symbol(data))

        if self.echo:
            self.transport.sendto(data, addr)

    def decode_symbol(self, data) -> int:
        return int.from_bytes(data, byteorder='little')

    def new_synchronizer(self, addr) -> Queue:
        print(f'Started observing flow: {addr}')
        queue = Queue()
        synchronizer = Synchronizer(get_seed(addr), queue)
        _ = ensure_future(synchronizer.synchronize())
        return queue


loop = get_event_loop()
print(f'Starting UDP server, listening on {local_ip}:{local_port}')
listen = loop.create_datagram_endpoint(
    SequenceServerProtocol, local_addr=(local_ip, local_port))
transport, protocol = loop.run_until_complete(listen)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()
