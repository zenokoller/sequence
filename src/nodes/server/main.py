import asyncio
import logging
from argparse import ArgumentParser
from functools import partial

from nodes.server.protocol import get_server_protocol
from reporter.utils import create_reporter, start_reporter
from sequence.seed import seed_from_addresses, seed_from_flow_id
from sequence.sequence import get_sequence_cls, default_sequence_args
from synchronizer.synchronizer import default_synchronize_args, get_synchronize_fn
from utils.asyncio import cancel_pending_tasks
from utils.env import get_server_host
from utils.logging import setup_logger, disable_logging
from utils.override_defaults import override_defaults

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
parser.add_argument('--recovery_batch_size', type=int,
                    help='number of packets to accumulate until first recovery attempt')
parser.add_argument('--recovery_range_length', type=int,
                    help='length of sequence search space in recovery')
args = parser.parse_args()

# Configure logging
if args.nolog:
    disable_logging()
else:
    setup_logger(log_dir=args.log_dir, file_level=logging.INFO)

# Configure server
local_ip = get_server_host()
local_port = args.local_port

seed_fn = seed_from_flow_id
get_seed = partial(seed_from_addresses, seed_fn, recv_addr=(local_ip, local_port))

sequence_args = override_defaults(default_sequence_args, vars(args))
sequence_cls = get_sequence_cls(**sequence_args)

reporter_args = args.reporter_args.split()
reporter = create_reporter(args.reporter_name, *reporter_args)
reporter_queue = start_reporter(reporter)

synchronize_args = override_defaults(default_synchronize_args, vars(args))
synchronize = get_synchronize_fn(**synchronize_args)
server_protocol = get_server_protocol(get_seed, sequence_cls, synchronize, reporter_queue,
                                      report_received=args.report_received)

# Print settings
logging.info(f'Starting UDP server, listening on {local_ip}:{local_port}')
logging.info(f'sequence_args={sequence_args}')
logging.info(f'synchronize_args={synchronize_args}')
logging.info(f'reporter={args.reporter_name} {reporter_args}')
logging.info(f'report_received={args.report_received}')

# Start server
loop = asyncio.get_event_loop()
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
