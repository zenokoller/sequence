from argparse import ArgumentParser
from contextlib import closing
from time import sleep

from config.env import get_client_ip, get_server_ip
from sequence.seed import seed_from_flow_id
from sequence.send import send_default_sequence
from utils.create_socket import create_socket

DEFAULT_SENDING_RATE = 100  # Packets per second

parser = ArgumentParser()
parser.add_argument('local_port', type=int)
parser.add_argument('remote_port', type=int)
parser.add_argument('-r', '--rate', dest='rate', default=DEFAULT_SENDING_RATE, type=int,
                    help=f'Sending rate in packets. Default: {DEFAULT_SENDING_RATE}')
parser.add_argument('-o', '--offset', dest='offset', default=0, type=int,
                    help=f'Start offset of sequence. Default: 0')
args = parser.parse_args()


local_ip, remote_ip = get_client_ip(), get_server_ip()
local_port, remote_port = args.local_port, args.remote_port


with closing(create_socket(local_port=local_port)) as sock:
    seed = seed_from_flow_id(local_ip, local_port, remote_ip, remote_port)
    stop_sending = send_default_sequence(sock, (remote_ip, remote_port), seed=seed,
                                         sending_rate=args.rate, offset=args.offset)

    while True:
        try:
            sleep(0.1)
    stop_sending()
