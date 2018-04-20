import hashlib


def seed_from_flow_id(src_ip: str, src_port: int, dst_ip: str, dst_port: int) -> str:
    md5 = hashlib.md5()
    md5.update(''.join([src_ip, str(src_port), dst_ip, str(dst_port)]).encode('utf-8'))
    return md5.hexdigest()
