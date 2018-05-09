import asyncio
import logging
import os
from argparse import ArgumentParser
from functools import partial

import yaml

from nodes.server.protocol import get_server_protocol
from reporter.get_reporter import get_reporter
from sequence.seed import seed_from_addresses, seed_functions
from sequence.sequence import get_sequence_cls
from utils.asyncio import cancel_pending_tasks
from utils.env import get_server_ip
from utils.logging import setup_logger, disable_logging

DEFAULT_CONFIG = 'default'

parser = ArgumentParser()
parser.add_argument('local_port', type=int)

parser.add_argument('-e', '--echo', action='store_true')
parser.add_argument('-n', '--nolog', action='store_true')
parser.add_argument('-l', '--log_dir', dest='log_dir', default=None, type=str,
                    help=f'Path to log directory. Default: None')
parser.add_argument('-c', '--config', default=DEFAULT_CONFIG, type=str,
                    help=f'Name of config file. Default: {DEFAULT_CONFIG}')
args = parser.parse_args()

# Configure logging
if args.nolog:
    disable_logging()
else:
    setup_logger(log_dir=args.log_dir, file_level=logging.INFO)

# Configure server
local_ip = get_server_ip()
local_port = args.local_port

config_path = os.path.join(os.path.dirname(__file__), f'config/{args.config}.yml')
with open(config_path, 'r') as config_file:
    config = yaml.load(config_file)
seed_fn = seed_functions[config['seed_fn']]
get_seed = partial(seed_from_addresses, seed_fn, recv_addr=(local_ip, local_port))
sequence_cls = get_sequence_cls(**config['sequence'])
reporter = get_reporter(config['reporter']['name'], *config['reporter']['args'])
server_protocol = get_server_protocol(get_seed, sequence_cls, reporter)

#  Start reporter
loop = asyncio.get_event_loop()
loop.run_until_complete(reporter.start())

# Start server
logging.info(f'Starting UDP server, listening on {local_ip}:{local_port}')
listen = loop.create_datagram_endpoint(server_protocol, local_addr=(local_ip, local_port))
transport, protocol = loop.run_until_complete(listen)

try:
    loop.run_forever()
except KeyboardInterrupt:
    logging.info('Stopping server...')
finally:
    transport.close()
    loop.run_until_complete(reporter.stop())
    cancel_pending_tasks()

loop.close()
