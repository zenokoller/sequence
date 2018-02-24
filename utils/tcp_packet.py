import hashlib
import plt as libtrace
from collections import namedtuple

TCPPacket = namedtuple('TCPPacket', ['timestamp', 'flow_hash', 'src_ip', 'dst_ip',
                                     'src_port', 'dst_port', 'seq_nr', 'ack_nr',
                                     'flags', 'ts_val', 'ts_ecr', 'payload_length'])


def get_flow_hash(packet: libtrace.packet) -> str:
    """
    Returns a hash representing a dicrection-agnostic TCP tuple.
    This way, we can group by packets from both directions.
    """
    src_ip, dst_ip = packet.ip.src_prefix, packet.ip.dst_prefix
    src_port, dst_port = packet.tcp.src_port, packet.tcp.dst_port
    flow_str = f'{src_ip}{src_port}{dst_ip}{dst_port}' if src_ip < dst_ip else f'{dst_ip}{dst_port}{src_ip}{src_port}'
    md5 = hashlib.md5()
    md5.update(flow_str.encode('utf8'))
    return md5.hexdigest()[:16]


TIMESTAMP_KIND = 8


def get_timestamps(tcp: libtrace.tcp) -> (int, int):
    ts = tcp.option(TIMESTAMP_KIND)
    if not ts or not isinstance(ts, bytearray):
        return (0, 0)
    return tuple(int.from_bytes(b, byteorder='big') for b in (ts[:4], ts[4:]))


def read_tcp_packet(packet: libtrace.packet) -> TCPPacket:
    tcp = packet.tcp
    timestamps = get_timestamps(tcp)
    return TCPPacket(timestamp=packet.time,
                     flow_hash=get_flow_hash(packet),
                     src_ip=packet.ip.src_prefix,
                     dst_ip=packet.ip.dst_prefix,
                     src_port=tcp.src_port,
                     dst_port=tcp.dst_port,
                     seq_nr=tcp.seq_nbr,
                     ack_nr=tcp.ack_nbr,
                     flags=tcp.flags,
                     ts_val=timestamps[0],
                     ts_ecr=timestamps[1],
                     payload_length=len(tcp.payload.data) if tcp.payload is not None else 0
                     )
