from argparse import ArgumentParser

from sequence.receive import receive_sequence

parser = ArgumentParser()
parser.add_argument('port', help='port to bind to', type=int)
args = parser.parse_args()

print(f'Listening on {args.port}')

receive_sequence(args.port)
