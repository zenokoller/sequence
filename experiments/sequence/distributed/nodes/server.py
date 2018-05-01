import asyncio
import logging
from argparse import ArgumentParser
from asyncio import Queue
from functools import partial
from typing import Dict

from config.env import get_server_ip
from config.logging import setup_logger
from detector.detector import detector
from sequence.seed import seed_from_addresses
from sequence.sequence import DefaultSequence
from synchronizer.synchronizer import synchronize
from utils.integer_codec import decode_symbol_with_offset
from utils.types import Address

parser = ArgumentParser()
parser.add_argument('local_port', type=int)
parser.add_argument('-e', '--echo', action='store_true')
parser.add_argument('-l', '--log_dir', dest='log_dir', default=None, type=str,
                    help=f'Path to log directory. Default: None')
args = parser.parse_args()

setup_logger(log_dir=args.log_dir, file_level=logging.INFO)
recv_logger = setup_logger('received', log_dir=args.log_dir, format='%(message)s')

local_ip = get_server_ip()
local_port = args.local_port

get_seed = partial(seed_from_addresses, recv_addr=(local_ip, local_port))

sequence_cls = DefaultSequence
report = lambda events: print(events)


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
            queue = self.start_sync_and_detector(addr)
            self.queues[addr] = queue

        symbol, offset = decode_symbol_with_offset(data)
        queue.put_nowait(symbol)
        recv_logger.debug(f'{offset}; {symbol}')

        if self.echo:
            self.transport.sendto(data, addr)

    def start_sync_and_detector(self, addr) -> Queue:
        seed = get_seed(addr)
        logging.info(f'Start observing flow; addr={addr}; seed={seed}')
        symbol_queue, event_queue = Queue(), Queue()
        _ = asyncio.ensure_future(synchronize(seed, symbol_queue, event_queue, sequence_cls))
        _ = asyncio.ensure_future(detector(seed, event_queue, sequence_cls, report))
        return symbol_queue


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
