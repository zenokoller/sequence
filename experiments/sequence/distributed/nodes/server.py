from argparse import ArgumentParser
from functools import partial

from process_flows.demux_socket import default_demux_socket
from sequence.seed import seed_from_flow_id
from utils.create_socket import create_socket
from utils.ip import get_my_ip

parser = ArgumentParser()
parser.add_argument('port', help='port to bind to', type=int)
args = parser.parse_args()

src_addr, src_port = get_my_ip(), args.port


def seed_from_addr_port(dst_addr: str, dst_port: int):
    return seed_from_flow_id(src_addr, src_port, dst_addr, dst_port)


demux_socket = partial(default_demux_socket, seed_from_addr_port=seed_from_addr_port)

print(f'Server: Listening on {src_addr}:{src_port}')
sock = create_socket(src_port)
try:
    demux_socket(sock)
except KeyboardInterrupt:
    print('Stopping server...')
sock.close()
