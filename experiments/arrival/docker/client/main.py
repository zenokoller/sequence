import sys
from argparse import ArgumentParser

sys.path.insert(0, '/root/python')
from client.ip import get_src_ip
from client.seed import get_seed
from client.send_sequence import send_random_sequence

DEFAULT_SENDING_RATE = 100  # Packets per second

parser = ArgumentParser()

parser.add_argument('src_port', help='source port', type=int)
parser.add_argument('dst_ip', help='destination IP address')
parser.add_argument('dst_port', help='destination port', type=int)
parser.add_argument('-r', '--rate', dest='rate', default=DEFAULT_SENDING_RATE, type=int,
                    help=f'sending rate in packets. Default: {DEFAULT_SENDING_RATE}')

args = parser.parse_args()

print(f'Sending to {args.dst_ip}:{args.dst_port}')
seed = get_seed(get_src_ip(), args.src_port, args.dst_ip, args.dst_port)
send_random_sequence(args.src_port, args.dst_ip, args.dst_port, seed=seed, sending_rate=args.rate)
