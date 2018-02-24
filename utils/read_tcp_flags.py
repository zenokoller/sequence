from typing import List

FLAGS = {1: 'FIN', 2: 'SYN', 4: 'RST', 8: 'PSH', 16: 'ACK', 32: 'URG'}


def read_tcp_flags(flag_int: int) -> List[str]:
    return [flag for test, flag in FLAGS.items() if flag_int & test]

print(read_tcp_flags(18))
