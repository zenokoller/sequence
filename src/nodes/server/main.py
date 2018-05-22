import asyncio
import logging
from argparse import ArgumentParser
from functools import partial

from nodes.server.protocol import get_server_protocol
from reporter.utils import create_reporter, start_reporter
from sequence.seed import seed_from_addresses, seed_from_flow_id
from sequence.sequence import get_sequence_cls, override_sequence_args
from utils.asyncio import cancel_pending_tasks
from utils.env import get_server_ip
from utils.logging import setup_logger, disable_logging

DEFAULT_CONFIG = 'default'

parser = ArgumentParser()
parser.add_argument('local_port', type=int)
parser.add_argument('-e', '--echo', action='store_true')
parser.add_argument('-n', '--nolog', action='store_true')
parser.add_argument('-l', '--log_dir', dest='log_dir', default=None, type=str,
                    help='path to log directory; default: None')
parser.add_argument('-p', '--period', type=int, help='sequence period')
parser.add_argument('-s', '--symbol_bits', type=int, help='number of bits for each symbol')
parser.add_argument('--reporter_name', type=str, help='reporter name, see reporter.utils')
parser.add_argument('--reporter_args', type=str, default='',
                    help='space-separated reporter args in quotes')
parser.add_argument('--report_received', action='store_true')
args = parser.parse_args()

# Configure logging
if args.nolog:
    disable_logging()
else:
    setup_logger(log_dir=args.log_dir, file_level=logging.INFO)

# Configure server
local_ip = get_server_ip()
local_port = args.local_port

seed_fn = seed_from_flow_id
get_seed = partial(seed_from_addresses, seed_fn, recv_addr=(local_ip, local_port))

sequence_args = override_sequence_args(vars(args))
sequence_cls = get_sequence_cls(**sequence_args)

reporter = create_reporter(args.reporter_name, *args.reporter_args.split())
reporter_queue = start_reporter(reporter)

server_protocol = get_server_protocol(get_seed, sequence_cls, reporter_queue,
                                      report_received=args.report_received)

# Start server
loop = asyncio.get_event_loop()
logging.info(f'Starting UDP server, listening on {local_ip}:{local_port}')
listen = loop.create_datagram_endpoint(server_protocol, local_addr=(local_ip, local_port))
transport, protocol = loop.run_until_complete(listen)

try:
    loop.run_forever()
except KeyboardInterrupt:
    logging.info('Stopping server...')
finally:
    transport.close()
    reporter_queue.join()
    loop.run_until_complete(reporter.cleanup())
    cancel_pending_tasks()

loop.close()
