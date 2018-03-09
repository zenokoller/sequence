from typing import List

FLAGS = {1: 'FIN', 2: 'SYN', 4: 'RST', 8: 'PSH', 16: 'ACK', 32: 'URG'}


def read_tcp_flags(flags: int) -> List[str]:
    return [flag for test, flag in FLAGS.items() if flags & test]


def is_fin_set(flags: int) -> bool:
    return bool(flags & 1)
