import asyncio
import logging
import os
from argparse import ArgumentParser

import aioprocessing
import yaml

from nodes.router.demultiplex_flows import get_demultiplex_flow_fn
from nodes.router.libtrace_process import try_run_libtrace
from reporter.get_reporter import get_reporter
from sequence.seed import seed_functions
from sequence.sequence import get_sequence_cls
from utils.asyncio import cancel_pending_tasks
from utils.logging import setup_logger, disable_logging

DEFAULT_IN_URI = 'int:eth0'
DEFAULT_CONFIG = 'default'

parser = ArgumentParser()
parser.add_argument('-i', '--in_uri', help='libtrace URI of interface to observe',
                    default=DEFAULT_IN_URI)
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

# Configure observer
config_path = os.path.join(os.path.dirname(__file__), f'config/{args.config}.yml')
with open(config_path, 'r') as config_file:
    config = yaml.load(config_file)
seed_from_flow_id = seed_functions[config['seed_fn']]
sequence_cls = get_sequence_cls(**config['sequence'])
reporter = get_reporter(config['reporter']['name'], *config['reporter']['args'])

demultiplex_flows = get_demultiplex_flow_fn(seed_from_flow_id, sequence_cls, reporter)

# Start libtrace process
queue = aioprocessing.AioQueue()
lt_process = aioprocessing.AioProcess(target=try_run_libtrace, args=(args.in_uri, queue))
lt_process.start()

#  Start reporter
loop = asyncio.get_event_loop()
loop.run_until_complete(reporter.start())

# Start observing flows
logging.info('Starting UDP observer.')
try:
    loop.run_until_complete(demultiplex_flows(queue))
except KeyboardInterrupt:
    logging.info('Stopping observer...')
finally:
    loop.run_until_complete(reporter.stop())
    pending = asyncio.Task.all_tasks()
    cancel_pending_tasks()

loop.run_until_complete(lt_process.coro_join())
loop.close()