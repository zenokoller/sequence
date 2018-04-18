import plt as libtrace
from argparse import ArgumentParser

from utils.managed_trace import managed_trace

DEFAULT_IN_URI = 'int:eth0'

parser = ArgumentParser()
parser.add_argument('-i', '--in_uri', help='libtrace URI of interface to observe',
                    default=DEFAULT_IN_URI)
args = parser.parse_args()

print(f'Sniffing on interface: {args.in_uri}')

filter_ = libtrace.filter('udp')  # TODO: Is this even working?
with managed_trace(args.in_uri) as trace:
    trace.conf_filter(filter_)
    raise NotImplementedError('demux_trace here')
