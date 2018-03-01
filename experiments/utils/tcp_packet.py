import hashlib
import plt as libtrace
from collections import namedtuple
from typing import Optional, Tuple

TCPPacket = namedtuple('TCPPacket', ['timestamp', 'flow_hash', 'direction', 'seq_nr', 'ack_nr',
                                     'flags', 'ts_val', 'ts_ecr', 'payload_length'])


def get_flow_hash_with_direction(packet: libtrace.packet) -> Tuple[str, bool]:
    """
    Returns a tuple `(flow_hash, direction)` where `flow_hash` represents a direction-agnostic
    TCP tuple by which we can group packets from both directions and `direction` == True iff
    src_ip < dst_ip.
    """
    ip = packet.ip if packet.ip is not None else packet.ip6
    src_ip, dst_ip = ip.src_prefix, ip.dst_prefix
    src_port, dst_port = packet.tcp.src_port, packet.tcp.dst_port
    direction = src_ip < dst_ip
    flow_str = f'{src_ip}{src_port}{dst_ip}{dst_port}' if direction else \
        f'{dst_ip}{dst_port}{src_ip}{src_port}'
    md5 = hashlib.md5()
    md5.update(flow_str.encode('utf8'))
    return md5.hexdigest()[:16], direction


TIMESTAMP_KIND = 8


def get_timestamps(tcp: libtrace.tcp) -> (int, int):
    ts = tcp.option(TIMESTAMP_KIND)
    if not ts or not isinstance(ts, bytearray):
        return 0, 0
    return tuple(int.from_bytes(b, byteorder='big') for b in (ts[:4], ts[4:]))


def read_tcp_packet(packet: libtrace.packet) -> TCPPacket:
    tcp = packet.tcp
    flow_hash, direction = get_flow_hash_with_direction(packet)
    timestamps = get_timestamps(tcp)
    return TCPPacket(timestamp=packet.time,
                     flow_hash=flow_hash,
                     direction=direction,
                     seq_nr=tcp.seq_nbr,
                     ack_nr=tcp.ack_nbr,
                     flags=tcp.flags,
                     ts_val=timestamps[0],
                     ts_ecr=timestamps[1],
                     payload_length=len(tcp.payload.data) if tcp.payload is not None else 0)


def try_read_tcp_packet(packet: libtrace.packet) -> Optional[TCPPacket]:
    try:
        return read_tcp_packet(packet)
    except ValueError as e:
        return None
