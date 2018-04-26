import asyncio
import logging
from argparse import ArgumentParser
from asyncio import Queue
from functools import partial
from typing import Dict

from config.env import get_server_ip
from sequence.seed import seed_from_addresses
from synchronizer.synchronizer import DefaultSynchronizer
from config.logging import configure_logging
from utils.types import Address

parser = ArgumentParser()
parser.add_argument('local_port', type=int)
parser.add_argument('-e', '--echo', action='store_true')
parser.add_argument('-l', '--log_path', dest='log_path', default=None, type=str,
                    help=f'Path to log file. Default: None')
args = parser.parse_args()

configure_logging(log_path=args.log_path)

local_ip = get_server_ip()
local_port = args.local_port

get_seed = partial(seed_from_addresses, recv_addr=(local_ip, local_port))
Synchronizer = DefaultSynchronizer


class SequenceServerProtocol:
    def __init__(self, echo=False):
        self.echo = echo
        self.transport = None
        self.queues: Dict[Address: Queue] = {}

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        if exc is not None:
            logging.warning(f'Connection lost: {exc}')

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
        logging.info(f'Start observing flow: {addr}')
        queue = Queue()
        synchronizer = Synchronizer(get_seed(addr), queue)
        _ = asyncio.ensure_future(synchronizer.synchronize())
        return queue


loop = asyncio.get_event_loop()
logging.info(f'Starting UDP server, listening on {local_ip}:{local_port}')
listen = loop.create_datagram_endpoint(
    SequenceServerProtocol, local_addr=(local_ip, local_port))
transport, protocol = loop.run_until_complete(listen)

try:
    loop.run_forever()
except KeyboardInterrupt:
    logging.info('Stopping server...')
finally:
    transport.close()
    pending = asyncio.Task.all_tasks()
    try:
        loop.run_until_complete(asyncio.gather(*pending))
    except:
        pass
loop.close()
