import logging
import os
from argparse import ArgumentParser
from contextlib import closing
from functools import partial
from time import sleep

import yaml

from sequence.seed import seed_functions
from sequence.send import send_sequence
from sequence.sequence import get_sequence_cls
from utils.create_socket import create_socket
from utils.env import get_client_ip, get_server_ip
from utils.logging import setup_logger, disable_logging

DEFAULT_SENDING_RATE = 100  # Packets per second
DEFAULT_OFFSET = 0
DEFAULT_CONFIG = 'default'

parser = ArgumentParser()
parser.add_argument('local_port', type=int)
parser.add_argument('remote_port', type=int)
parser.add_argument('-r', '--rate', type=int, help=f'Sending rate in packets.')
parser.add_argument('-o', '--offset', type=int, help=f'Start offset of sequence.')
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
    setup_logger(log_dir=args.log_dir)

# Configure client
local_ip, remote_ip = get_client_ip(), get_server_ip()
local_port, remote_port = args.local_port, args.remote_port

config_path = os.path.join(os.path.dirname(__file__), f'config/{args.config}.yml')
with open(config_path, 'r') as config_file:
    config = yaml.load(config_file)
seed_fn = seed_functions[config['seed_fn']]
sending_rate = args.rate or config['sending_rate'] or DEFAULT_SENDING_RATE
offset = args.offset or config['offset'] or DEFAULT_OFFSET
send_sequence = partial(send_sequence, sequence_cls=get_sequence_cls(**config['sequence']))

# Start client
logging.info(f'Client: Sending on {local_ip}:{local_port} -> {remote_ip}:{remote_port}')
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
