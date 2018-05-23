import asyncio
import logging
from argparse import ArgumentParser

import aioprocessing

from nodes.router.demultiplex_flows import get_demultiplex_flow_fn
from nodes.router.libtrace_process import try_run_libtrace
from reporter.utils import create_reporter, start_reporter
from sequence.seed import seed_from_flow_id
from sequence.sequence import get_sequence_cls, default_sequence_args
from synchronizer.synchronizer import default_synchronize_args, get_synchronize_fn
from utils.asyncio import cancel_pending_tasks
from utils.logging import setup_logger, disable_logging
from utils.override_defaults import override_defaults

DEFAULT_IN_URI = 'int:eth0'

parser = ArgumentParser()
parser.add_argument('-i', '--in_uri', help='libtrace URI of interface to observe',
                    default=DEFAULT_IN_URI)
parser.add_argument('-l', '--log_dir', dest='log_dir', type=str,
                    help='path to log directory; default: None')
parser.add_argument('-n', '--nolog', action='store_true')
parser.add_argument('-p', '--period', type=int, help='sequence period')
parser.add_argument('-s', '--symbol_bits', type=int, help='number of bits for each symbol')
parser.add_argument('--reporter_name', type=str, help='reporter name, see reporter.utils')
parser.add_argument('--reporter_args', type=str, default='',
                    help='space-separated reporter args in quotes')
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

# Configure observer
seed_fn = seed_from_flow_id

sequence_args = override_defaults(default_sequence_args, vars(args))
sequence_cls = get_sequence_cls(**sequence_args)

reporter_args = args.reporter_args.split()
reporter = create_reporter(args.reporter_name, *reporter_args)
reporter_queue = start_reporter(reporter)

synchronize_args = override_defaults(default_synchronize_args, vars(args))
synchronize = get_synchronize_fn(**synchronize_args)
demultiplex_flows = get_demultiplex_flow_fn(seed_fn, sequence_cls, synchronize, reporter_queue)

# Print settings
logging.info('Starting UDP observer...')
logging.info(f'sequence_args={sequence_args}')
logging.info(f'reporter={args.reporter_name} {reporter_args}')

# Start libtrace process
queue = aioprocessing.AioQueue()
lt_process = aioprocessing.AioProcess(target=try_run_libtrace, args=(args.in_uri, queue))
lt_process.start()

# Start observing flows
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(demultiplex_flows(queue))
except KeyboardInterrupt:
    logging.info('Stopping observer...')
finally:
    reporter_queue.join()
    loop.run_until_complete(reporter.cleanup())
    pending = asyncio.Task.all_tasks()
    cancel_pending_tasks()

loop.run_until_complete(lt_process.coro_join())
loop.close()
