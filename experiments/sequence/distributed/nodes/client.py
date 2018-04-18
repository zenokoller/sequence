from argparse import ArgumentParser
from time import sleep

from sequence.seed import seed_from_flow_id
from sequence.send import send_random_sequence
from utils.create_socket import create_socket
from utils.ip import get_my_ip

DEFAULT_SENDING_RATE = 100  # Packets per second

parser = ArgumentParser()
parser.add_argument('src_port', help='source port', type=int)
parser.add_argument('dst_ip', help='destination IP address')
parser.add_argument('dst_port', help='destination port', type=int)
parser.add_argument('-r', '--rate', dest='rate', default=DEFAULT_SENDING_RATE, type=int,
                    help=f'sending rate in packets. Default: {DEFAULT_SENDING_RATE}')
args = parser.parse_args()

src_ip = get_my_ip()
print(f'Client: Sending on {src_ip}:{args.src_port} -> {args.dst_ip}:{args.dst_port}')

sock = create_socket(src_port=args.src_port)
dest = args.dst_ip, args.dst_port
seed = seed_from_flow_id(src_ip, args.src_port, args.dst_ip, args.dst_port)
stop = send_random_sequence(sock, dest, seed=seed, sending_rate=args.rate)

while True:
    try:
        sleep(0.1)
    except KeyboardInterrupt:
        print('Stopping client...')

stop()
sock.close()
