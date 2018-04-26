import logging
from argparse import ArgumentParser
from contextlib import closing
from time import sleep

from config.env import get_client_ip, get_server_ip
from sequence.seed import seed_from_flow_id
from sequence.send import send_default_sequence
from config.logging import configure_logging
from utils.create_socket import create_socket

DEFAULT_SENDING_RATE = 100  # Packets per second

parser = ArgumentParser()
parser.add_argument('local_port', type=int)
parser.add_argument('remote_port', type=int)
parser.add_argument('-r', '--rate', dest='rate', default=DEFAULT_SENDING_RATE, type=int,
                    help=f'Sending rate in packets. Default: {DEFAULT_SENDING_RATE}')
parser.add_argument('-o', '--offset', dest='offset', default=0, type=int,
                    help=f'Start offset of sequence. Default: 0')
parser.add_argument('-l', '--log_path', dest='log_path', default=None, type=str,
                    help=f'Path to log file. Default: None')
args = parser.parse_args()

configure_logging(log_path=args.log_path)

local_ip, remote_ip = get_client_ip(), get_server_ip()
local_port, remote_port = args.local_port, args.remote_port

logging.info(f'Client: Sending on {local_ip}:{local_port} -> {remote_ip}:{remote_port}')

with closing(create_socket(local_port=local_port)) as sock:
    seed = seed_from_flow_id(local_ip, local_port, remote_ip, remote_port)
    logging.debug(f'Seed: {seed}')
    stop_sending = send_default_sequence(sock, (remote_ip, remote_port), seed=seed,
                                         sending_rate=args.rate, offset=args.offset)

    while True:
        try:
            sleep(0.1)
        except KeyboardInterrupt:
            logging.info('Stopping client...')
            break
    stop_sending()
