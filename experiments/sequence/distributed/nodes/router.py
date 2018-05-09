import asyncio
import logging
import plt as libtrace
from argparse import ArgumentParser
from typing import Dict

import aioprocessing
import yaml

from reporter.get_reporter import get_reporter
from sequence.sequence import get_sequence_cls
from utils.logging import setup_logger, disable_logging
from detector.detector import detector
from sequence.seed import seed_from_flow_id, seed_functions
from synchronizer.synchronizer import synchronize
from utils.integer_codec import decode_symbol_with_offset
from utils.managed_trace import managed_trace
from utils.types import FlowId

DEFAULT_IN_URI = 'int:eth0'

parser = ArgumentParser()
parser.add_argument('-i', '--in_uri', help='libtrace URI of interface to observe',
                    default=DEFAULT_IN_URI)
parser.add_argument('-n', '--nolog', action='store_true')
parser.add_argument('-l', '--log_dir', dest='log_dir', default=None, type=str,
                    help=f'Path to log directory. Default: None')
parser.add_argument('-c', '--config_path', default='config/router/default.yml', type=str,
                    help='Path of config file.')
args = parser.parse_args()

# Configure logging
if args.nolog:
    disable_logging()
else:
    setup_logger(log_dir=args.log_dir, file_level=logging.INFO)

# Configure observer
with open(args.config_path, 'r') as config_file:
    config = yaml.load(config_file)
seed_fn = seed_functions[config['seed_fn']]
sequence_cls = get_sequence_cls(**config['sequence'])
reporter = get_reporter(config['reporter']['name'], *config['reporter']['args'])


def run_libtrace(queue: aioprocessing.Queue):
    print(f'Sniffing on interface: {args.in_uri}')
    filter_ = libtrace.filter('udp')
    with managed_trace(args.in_uri) as trace:
        trace.conf_filter(filter_)
        for packet in trace:
            ip, udp = packet.ip, packet.udp
            if ip is None or udp is None:
                continue

            src_ip, dst_ip = map(str, (ip.src_prefix, ip.dst_prefix))
            src_port, dst_port = udp.src_port, udp.dst_port
            flow_id = (src_ip, src_port, dst_ip, dst_port)

            symbol, _ = decode_symbol_with_offset(udp.payload.data)

            queue.put((flow_id, symbol, packet.erf_time))


async def demultiplex_flows(in_queue: aioprocessing.Queue):
    out_queues: Dict[FlowId:asyncio.Queue] = {}

    while True:
        flow_id, symbol, time = await in_queue.coro_get()
        out_queue = out_queues.get(flow_id, None)
        if out_queue is None:
            out_queue = start_sync_and_detector(flow_id)
            out_queues[flow_id] = out_queue

        await out_queue.put(symbol)


def start_sync_and_detector(flow_id) -> asyncio.Queue:
    seed = seed_fn(*flow_id)
    logging.info(f'Start observing flow; flow_id={flow_id}; seed={seed}')
    symbol_queue, event_queue = asyncio.Queue(), asyncio.Queue()
    _ = asyncio.ensure_future(synchronize(seed, symbol_queue, event_queue, sequence_cls))
    _ = asyncio.ensure_future(detector(seed, event_queue, sequence_cls, reporter))
    return symbol_queue


loop = asyncio.get_event_loop()

# Start libtrace process
queue = aioprocessing.AioQueue()
lt_process = aioprocessing.AioProcess(target=run_libtrace, args=(queue,))
lt_process.start()

#  Start reporter
loop.run_until_complete(reporter.start())

# Start observing flows
logging.info('Starting UDP observer')
try:
    loop.run_until_complete(demultiplex_flows(queue))
except KeyboardInterrupt:
    logging.info('Stopping observer...')
finally:
    reporter.stop()
    pending = asyncio.Task.all_tasks()
    try:
        loop.run_until_complete(asyncio.gather(*pending))
    except:
        pass
loop.close()
lt_process.coro_join()
