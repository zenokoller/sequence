def seed_from_flow_id(src_ip: str, src_port: int, dst_ip: str, dst_port: int) -> int:
    return hash(''.join([src_ip, str(src_port), dst_ip, str(dst_port)]))
