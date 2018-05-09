import logging
import plt as libtrace

import aioprocessing

from utils.integer_codec import decode_symbol_with_offset
from utils.managed_trace import managed_trace


def run_libtrace(in_uri: str, queue: aioprocessing.Queue):
    """Run librace using interface `in_uri`, sending `(flow_id, symbol, packet_clock)` triples to
    the given queue."""
    logging.info(f'Sniffing on interface: {in_uri}')
    filter_ = libtrace.filter('udp')
    with managed_trace(in_uri) as trace:
        trace.conf_filter(filter_)
        for packet in trace:
            ip, udp = packet.ip, packet.udp
            if ip is None or udp is None:
                continue

            src_ip, dst_ip = map(str, (ip.src_prefix, ip.dst_prefix))
            src_port, dst_port = udp.src_port, udp.dst_port
            flow_id = (src_ip, src_port, dst_ip, dst_port)

            symbol, _ = decode_symbol_with_offset(udp.payload.data)

            queue.put((flow_id, symbol, packet.erf_time))
