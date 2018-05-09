import asyncio
import logging
from argparse import ArgumentParser
from asyncio import Queue
from functools import partial
from typing import Dict

import yaml

from detector.detector import detector
from reporter.get_reporter import get_reporter
from sequence.seed import seed_from_addresses, seed_functions
from sequence.sequence import get_sequence_cls
from synchronizer.synchronizer import synchronize
from utils.env import get_server_ip
from utils.integer_codec import decode_symbol_with_offset
from utils.logging import setup_logger, disable_logging
from utils.types import Address

DEFAULT_CONFIG_PATH = 'config/server/default.yml'

parser = ArgumentParser()
parser.add_argument('local_port', type=int)

parser.add_argument('-e', '--echo', action='store_true')
parser.add_argument('-n', '--nolog', action='store_true')
parser.add_argument('-l', '--log_dir', dest='log_dir', default=None, type=str,
                    help=f'Path to log directory. Default: None')
parser.add_argument('-c', '--config_path', default=DEFAULT_CONFIG_PATH, type=str,
                    help=f'Path to config file. Default: {DEFAULT_CONFIG_PATH}')
args = parser.parse_args()

# Configure logging
if args.nolog:
    disable_logging()
else:
    setup_logger(log_dir=args.log_dir, file_level=logging.INFO)

# Configure server
local_ip = get_server_ip()
local_port = args.local_port

with open(args.config_path, 'r') as config_file:
    config = yaml.load(config_file)
seed_fn = seed_functions[config['seed_fn']]
get_seed = partial(seed_from_addresses, seed_fn, recv_addr=(local_ip, local_port))
sequence_cls = get_sequence_cls(**config['sequence'])
reporter = get_reporter(config['reporter']['name'], *config['reporter']['args'])


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

        if self.echo:
            self.transport.sendto(data, addr)

    def start_sync_and_detector(self, addr) -> Queue:
        seed = get_seed(addr)
        logging.info(f'Start observing flow; addr={addr}; seed={seed}')
        symbol_queue, event_queue = Queue(), Queue()
        _ = asyncio.ensure_future(synchronize(seed, symbol_queue, event_queue, sequence_cls))
        _ = asyncio.ensure_future(detector(seed, event_queue, sequence_cls, reporter))
        return symbol_queue


loop = asyncio.get_event_loop()

#  Start reporter
loop.run_until_complete(reporter.start())

# Start server
logging.info(f'Starting UDP server, listening on {local_ip}:{local_port}')
listen = loop.create_datagram_endpoint(SequenceServerProtocol, local_addr=(local_ip, local_port))
transport, protocol = loop.run_until_complete(listen)

try:
    loop.run_forever()
except KeyboardInterrupt:
    logging.info('Stopping server...')
finally:
    transport.close()
    reporter.stop()
    pending = asyncio.Task.all_tasks()
    try:
        loop.run_until_complete(asyncio.gather(*pending))
    except:
        pass
loop.close()
