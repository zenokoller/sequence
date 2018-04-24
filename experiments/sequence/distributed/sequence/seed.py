import hashlib

from utils.types import Address


def seed_from_addresses(send_addr: Address = None, recv_addr: Address = None) -> int:
    return seed_from_flow_id(*send_addr, *recv_addr)


def seed_from_flow_id(src_ip: str, src_port: int, dst_ip: str, dst_port: int) -> int:
    md5 = hashlib.md5()
    md5.update(''.join([src_ip, str(src_port), dst_ip, str(dst_port)]).encode('utf-8'))
    return int(md5.hexdigest(), 16)
