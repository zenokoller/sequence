import logging
from argparse import ArgumentParser
from contextlib import closing
from functools import partial
from time import sleep

from sequence.seed import seed_from_flow_id
from sequence.send import send_sequence
from sequence.sequence import get_sequence_cls, override_sequence_args
from utils.create_socket import create_socket
from utils.env import get_client_ip, get_server_ip
from utils.logging import setup_logger, disable_logging

DEFAULT_SENDING_RATE = 100  # Packets per second
DEFAULT_OFFSET = 0
DEFAULT_CONFIG = 'default'

parser = ArgumentParser()
parser.add_argument('local_port', type=int)
parser.add_argument('remote_port', type=int)
parser.add_argument('-l', '--log_dir', dest='log_dir', default=None, type=str,
                    help=f'path to log directory; default: None')
parser.add_argument('-n', '--nolog', action='store_true')
parser.add_argument('-o', '--offset', type=int, help='start offset of sequence')
parser.add_argument('-p', '--period', type=int, help='sequence period')
parser.add_argument('-r', '--rate', type=int, help='sending rate in pps')
parser.add_argument('-s', '--symbol_bits', type=int, help='number of bits for each symbol')
args = parser.parse_args()

# Configure logging
if args.nolog:
    disable_logging()
else:
    setup_logger(log_dir=args.log_dir)

# Configure client
local_ip, remote_ip = get_client_ip(), get_server_ip()
local_port, remote_port = args.local_port, args.remote_port

seed_fn = seed_from_flow_id

sequence_args = override_sequence_args(vars(args))
sequence_cls = get_sequence_cls(**sequence_args)

send_sequence = partial(send_sequence, sequence_cls=sequence_cls)
sending_rate = args.rate or DEFAULT_SENDING_RATE
offset = args.offset or DEFAULT_OFFSET

# Start client
logging.info(f'Started client, sending on {local_ip}:{local_port} -> {remote_ip}:{remote_port}')
with closing(create_socket(local_port=local_port)) as sock:
    seed = seed_fn(local_ip, local_port, remote_ip, remote_port)
    logging.debug(f'Seed: {seed}')
    stop_sending = send_sequence(sock, (remote_ip, remote_port), seed=seed,
                                 sending_rate=sending_rate, offset=offset)

    while True:
        try:
            sleep(0.1)
        except KeyboardInterrupt:
            logging.info('Stopping client...')
            break
    stop_sending()
